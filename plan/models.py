# coding=utf-8
from django.db import models
from users.models import Athlete

class Plan(models.Model):
  name = models.CharField(max_length=250)
  creator = models.ForeignKey(Athlete, related_name='plans')

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return u'Plan: "%s" from %s' % (self.name, self.creator.username)

class PlanSession(models.Model):
  # Organisation
  plan = models.ForeignKey(Plan, related_name='sessions')
  week = models.IntegerField()
  day = models.IntegerField()

  # Dummy data, should be later specified
  # using a collections of PlanPart
  name = models.CharField(max_length=250)
