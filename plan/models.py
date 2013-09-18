from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class Plan(models.Model):
  name = models.CharField(max_length=250)
  creator = models.ForeignKey(User)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  start = models.DateField(null=True, blank=True) # Optional start date

  @models.permalink
  def get_absolute_url(self):
    return ('plan', (self.pk, ))

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
    date = self.plan.start
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
