from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from helpers import week_to_date, nameize
from base64 import b64encode
from hashlib import md5
from datetime import datetime

class Plan(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(max_length=20, db_index=True)
  creator = models.ForeignKey(User)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (('creator', 'slug',), )

  @models.permalink
  def get_absolute_url(self):
    return ('plan', (self.slug, ))

  def save(self, *args, **kwargs):
    # Init slug, based on name
    if not self.slug:
      self.slug = nameize(self.name)

    super(Plan, self).save(*args, **kwargs)

class PlanWeek(models.Model):
  plan = models.ForeignKey(Plan, related_name='weeks')
  order = models.IntegerField(default=0)

  class Meta:
    unique_together = (('plan', 'order',), )

  def get_days(self):
    '''
    List days in plan, using day id, date
     when available and session
    '''
    days = []
    date = None # To be used differently
    if date:
      date += timedelta(days=self.order * 7)

    for d in range(0,7):
      try:
        session = self.sessions.get(day=d)
      except:
        session = None
      days.append((d, date, session))
      if date:
        date += timedelta(days=1)

    return days

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
