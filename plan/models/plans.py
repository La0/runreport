# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import Athlete
from sport.models import Sport, SportWeek, SportDay, SportSession, SESSION_TYPES
from datetime import date, timedelta
from helpers import date_to_week
from coach.mail import MailBuilder
from plan.export import PlanPdfExporter
from interval.fields import IntervalField
from .apps import PlanApplied, PlanSessionApplied

class Plan(models.Model):
  name = models.CharField(max_length=250)
  creator = models.ForeignKey(Athlete, related_name='plans')

  # Dates
  start = models.DateField(null=True, blank=True) # A plan should start on monday
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return u'Plan: "%s" from %s' % (self.name, self.creator.username)

  @property
  def end(self):
    '''
    Calc the end date, on Sunday
    '''
    if not self.weeks_nb or not self.start:
      return self.start
    return self.start + timedelta(days=(7 * self.weeks_nb) - 1)

  @property
  def is_active(self):
    '''
    Plan is only active from start date
    until the nb of weeks specified
    '''
    if not self.start:
      return False

    today = date.today()
    return self.start <= today <= self.end

  @property
  def weeks_nb(self):
    '''
    Get current number of weeks in plan
    '''
    # Fetch prepared annotation (from api)
    nb = getattr(self, 'nb_weeks', 0)
    if nb:
      return nb + 1 # Max() needs an offset

    # Calc through aggregation (slow on lists)
    agg = self.sessions.aggregate(nb=models.Max('week'))
    if agg['nb'] is None:
      return 0
    return agg['nb'] + 1

  def update_weeks(self):
    '''
    Check the weeks described in sessions
    are still consecutive, starting from 0
    '''
    weeks = self.sessions.order_by('week').values_list('week', flat=True).distinct()
    for pos, week in enumerate(weeks):
      if pos != week:
        self.sessions.filter(week=week).update(week=pos)

  def calc_date(self, week, day):
    '''
    Calc the date of a day based on start date
    '''
    if not self.start:
      return None
    return self.start + timedelta(days=week*7+day)

  def publish(self, users):
    '''
    Publish a plan to specified users
    No verification on the users belonging
     to the creator here
    '''
    if not self.start:
      raise Exception("No start date on plan.")

    # Build the pdf export
    export = PlanPdfExporter(self)
    pdf = export.render()

    for u in users.all():
      # Save plan application
      pa, _ = PlanApplied.objects.get_or_create(user=u, plan=self)

      # Apply the sessions
      nb_applied = 0
      for s in self.sessions.all():
        try:
          s.apply(pa)
          nb_applied += 1
        except Exception, e:
          print 'Failed to apply plan session #%d : %s' % (s.pk, e)

      # Send an email to each user
      if nb_applied > 0:
        self.notify_athlete(u, pdf)

  def notify_athlete(self, user, pdf):
    '''
    Send an email to athlete
    with the plan attached
    '''
    # Context for html
    context = {
      'plan' : self,
      'user' : user,
    }

    # Build mail
    mb = MailBuilder('mail/plan.html', user.language)
    mb.subject = _(u'Training plan : %s') % (self.name, )
    mb.to = [user.email, ]
    mail = mb.build(context)

    # Attach Xls & send
    pdf_name = _('Training plan - %s.pdf') % self.name
    mail.attach(pdf_name, pdf, 'application/pdf')
    mail.send()

  def copy(self):
    '''
    Copy current plan & sessions
    '''

    # New plan, no start date
    data = {
      'name' : '%s - Copy' % (self.name, ),
      'creator' : self.creator,
    }
    plan = Plan.objects.create(**data)

    # Copy sessions
    for s in self.sessions.all():
      s.copy(plan)

    return plan

class PlanSession(models.Model):
  # Organisation
  plan = models.ForeignKey(Plan, related_name='sessions')
  week = models.IntegerField()
  day = models.IntegerField()

  # Dummy data, should be later specified
  # using a collections of PlanPart
  name = models.CharField(max_length=250)
  time = IntervalField(format='DHMSX', null=True, blank=True)
  distance = models.FloatField(null=True, blank=True)

  # Mappings to SportSession
  sport = models.ForeignKey(Sport)
  type = models.CharField(max_length=12, default='training', choices=SESSION_TYPES)

  # Conversation
  comments = models.OneToOneField('messages.Conversation', null=True, blank=True, related_name='plan_session')

  # Event
  place = models.ForeignKey('events.Place', null=True, blank=True, related_name='plan_sessions')
  hour = models.TimeField(null=True, blank=True)

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  @property
  def date(self):
    return self.plan.calc_date(self.week, self.day)

  def delete(self, *args, **kwargs):
    plan = self.plan # backup plan reference
    out = super(PlanSession, self).delete(*args, **kwargs) # actually delete the session
    plan.update_weeks() # Check weeks are still consecutive
    return out

  def copy(self, plan):
    '''
    Copy this session and attach it to new plan
    '''
    data = {
      'plan' : plan,
    }
    copy_fields = ('week', 'day', 'name', 'sport', 'type', )
    for f in copy_fields:
      data[f] = getattr(self, f)

    return PlanSession.objects.create(**data)

  def _build_day(self, user, date):
    # Internal used to create week & day hierarchy
    # Used on PSA move too (so date need to be specified)

    # Load week
    w, year = date_to_week(date)
    week,_ = SportWeek.objects.get_or_create(year=year, week=w, user=user)

    # Load day
    day,_ = SportDay.objects.get_or_create(week=week, date=date)

    return day

  def apply(self, application):
    '''
    Apply this plan session to a user
    '''
    if not self.date:
      raise Exception('No date to apply this session')

    day = self._build_day(application.user, self.date)

    # Check a session does not already have this plan session
    try:
      psa = PlanSessionApplied.objects.get(plan_session=self, sport_session__day=day)
    except PlanSessionApplied.DoesNotExist:
      psa = None

    if psa:
      # retrieve sport session
      session = psa.sport_session

      # Update applied session
      if psa.status == 'applied':
        psa.sport_session.name = self.name
        psa.sport_session.distance = self.distance
        psa.sport_session.time = self.time
        psa.sport_session.save()
    else:
      # Load session
      defaults = {
          'name' : self.name,
          'distance' : self.distance,
          'time' : self.time,
      }
      session,_ = SportSession.objects.get_or_create(sport=self.sport, day=day, type=self.type, defaults=defaults)

      # Apply plan session
      PlanSessionApplied.objects.create(plan_session=self, sport_session=session, application=application)

    # Copy all comments
    if self.comments:

      # Build conversation if needed
      if not session.comments_private:
        session.build_conversation('private')

      for c in self.comments.messages.all():
        c.copy(session.comments_private)
