# coding=utf-8
from django.db import models
from users.models import Athlete
from sport.models import Sport, SportWeek, SportDay, SportSession, SESSION_TYPES
from datetime import timedelta
from helpers import date_to_week

class Plan(models.Model):
  name = models.CharField(max_length=250)
  creator = models.ForeignKey(Athlete, related_name='plans')

  # Dates
  start = models.DateField(null=True, blank=True) # A plan should start on monday
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return u'Plan: "%s" from %s' % (self.name, self.creator.username)

  def get_weeks_nb(self):
    '''
    Get current number of weeks in plan
    '''
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

    for u in users.all():
      # Apply the sessions
      for s in self.sessions.all():
        try:
          s.apply(u)
        except Exception, e:
          print 'Failed to apply plan session #%d : %s' % (s.pk, e)

      # Send an email to each user
      # TODO

class PlanSession(models.Model):
  # Organisation
  plan = models.ForeignKey(Plan, related_name='sessions')
  week = models.IntegerField()
  day = models.IntegerField()

  # Dummy data, should be later specified
  # using a collections of PlanPart
  name = models.CharField(max_length=250)

  # Mappings to SportSession
  sport = models.ForeignKey(Sport)
  type = models.CharField(max_length=12, default='training', choices=SESSION_TYPES)

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

  def apply(self, user):
    '''
    Apply this plan session to a user
    '''
    if not self.date:
      raise Exception('No date to apply this session')

    # Load week
    w, year = date_to_week(self.date)
    week,_ = SportWeek.objects.get_or_create(year=year, week=w, user=user)

    # Load day
    day,_ = SportDay.objects.get_or_create(week=week, date=self.date)

    # Check a session does not already have this plan session
    if day.sessions.filter(plan_session=self).count() > 0:
      raise Exception('Already applied')

    # Load session
    session,_ = SportSession.objects.get_or_create(sport=self.sport, day=day, type=self.type, plan_session__isnull=True)

    # Apply plan session
    session.plan_session = self
    session.save()
