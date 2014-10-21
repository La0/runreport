# coding=utf-8
from django.db import models
from .organisation import SportDay, SportWeek
from .sport import SportSession, Sport
from users.models import Athlete
from datetime import datetime, time, timedelta
import os
import json
import hashlib
from coach.settings import GARMIN_DIR
import logging
from django.utils.timezone import utc
from helpers import date_to_week
from interval.fields import IntervalField

class GarminActivity(models.Model):
  garmin_id = models.IntegerField(unique=True)
  session = models.OneToOneField(SportSession, related_name='garmin_activity')
  sport = models.ForeignKey('Sport')
  user = models.ForeignKey(Athlete)
  name = models.CharField(max_length=255)
  time = IntervalField()
  distance = models.FloatField() # Kilometers
  speed = models.TimeField() # Time per kilometer
  md5_raw = models.CharField(max_length=32)
  md5_laps = models.CharField(max_length=32, null=True)
  md5_details = models.CharField(max_length=32, null=True)
  date = models.DateTimeField() # Date of the activity
  created = models.DateTimeField(auto_now_add=True) # Object creation
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'garmin_activity'
    app_label = 'sport'

  def __unicode__(self):
    return "%s: %s" % (self.garmin_id, self.name)

  def save(self, force_session=False, *args, **kwargs):
    # Search & Attach session
    if not self.session_id or force_session:
      self.attach_session()

    # Update session name ?
    if self.session_id and not self.session.name and self.name:
      self.session.name = self.name
      self.session.save()

    super(GarminActivity, self).save(*args, **kwargs)


  def get_url(self):
    return 'http://connect.garmin.com/activity/%s' % (self.garmin_id)

