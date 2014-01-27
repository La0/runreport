# coding=utf-8
from django.db import models
from users.models import Athlete
from datetime import timedelta
from helpers import week_to_date, nameize, date_to_week, date_to_day
from base64 import b64encode
from hashlib import md5
from datetime import datetime, date
from run.models import RunReport, RunSession
from coach.mail import MailBuilder

class Plan(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(max_length=20, db_index=True)
  creator = models.ForeignKey(Athlete)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  task = models.CharField(max_length=36, null=True, blank=True)

  class Meta:
    unique_together = (('creator', 'slug',), )

  @models.permalink
  def get_absolute_url(self):
    return ('plan', (self.slug, ))

  def __unicode__(self):
    return u'Plan: "%s" from %s' % (self.name, self.creator.username)

  def save(self, *args, **kwargs):
    # Init slug, based on name
    if not self.slug:
      self.slug = nameize(self.name)

    super(Plan, self).save(*args, **kwargs)

  def apply(self, start_date, users):
    '''
    Apply the plan to some users, since specified date
    '''
    failures = []
    for user in users:
      for week in self.weeks.order_by('order'):
        try:
          week.apply(start_date, user)
        except:
          failures.append(user)
          break

      # Create PlanUsage
      usage,_ = PlanUsage.objects.get_or_create(plan=self, user=user, start=start_date)
      if usage.mail_sent:
        continue # Don't send twice the mail about the same plan

      # Send mail to user
      mb = MailBuilder('mail/plan.html')
      context = {
        'plan' : self,
        'user' : user,
        'start_date' : start_date,
      }
      mb.subject = u'Plan d\'entraînement %s de %s %s' % (self.name, self.creator.first_name, self.creator.last_name)
      mb.to = [user.email]
      mail = mb.build(context)
      mail.send()

      # Update usage
      usage.mail_sent = datetime.now()
      usage.save()

    return failures

class PlanWeek(models.Model):
  plan = models.ForeignKey(Plan, related_name='weeks')
  order = models.IntegerField(default=0)

  class Meta:
    unique_together = (('plan', 'order',), )

  def get_days(self, start_date=None):
    '''
    List days in plan, using day id and session
    '''
    days = []

    if not start_date:
      start_date = date_to_day(date.today())
    for d in range(0,7):
      try:
        session = self.sessions.get(day=d)
      except:
        session = None

      # Build real day date, using start_date specified
      # or start from monday this week
      dt = start_date + timedelta(days=self.order*7 + d)

      days.append((d, dt, session))

    return days

  def apply(self, start_date, user):
    '''
    Apply to one user, from start date of whole plan
    '''
    start_date += timedelta(days=self.order*7)

    # Init a runreport for this week
    week, year = date_to_week(start_date)
    report, _ = RunReport.objects.get_or_create(user=user, year=year, week=week)

    # Attach the plan week to report
    if report.plan_week is not None and report.plan_week != self:
      raise Exception("A plan (%s) is already applied on report %s" % (report.plan_week.plan.name, report))
    report.plan_week = self
    report.save()

    # Apply Plan sessions to report
    for p in self.sessions.order_by('day'):
      p.apply(report)

class PlanSession(models.Model):
  week = models.ForeignKey(PlanWeek, related_name='sessions')
  day = models.IntegerField()
  name = models.CharField(max_length=250)
  distance = models.FloatField(null=True, blank=True)
  time = models.TimeField(null=True, blank=True)

  class Meta:
    unique_together = (('week', 'day',), )

  def get_date(self):
    '''
    Build a date to be used in templates
    '''
    d = week_to_date(2013, 1)
    d += timedelta(days=self.week.order * 7 + self.day)
    return d

  def apply(self, report):
    '''
    Apply a plan session to a report day
    '''
    day = report.get_date((self.day+1)%7) # in report date are stored using sunday as 0
    defaults = {
      'name' : self.name,
      'distance' : self.distance,
      'time' : self.time,
    }
    session, _ = RunSession.objects.get_or_create(report=report, date=day, defaults=defaults)
    session.plan_session = self
    session.save()

class PlanUsage(models.Model):
  plan = models.ForeignKey(Plan)
  user = models.ForeignKey(Athlete)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  start = models.DateTimeField() # Date of start of usage
  mail_sent = models.DateTimeField(null=True)
