# coding=utf-8
from django.db import models
from tracks.models import Track
from .organisation import SportDay, SportWeek
from .sport import SportSession, Sport
from users.models import Athlete
from datetime import datetime, time, timedelta
from django.contrib.gis.geos import LineString
import os
import json
import hashlib
from coach.settings import GARMIN_DIR
import logging
from django.utils.timezone import utc
from helpers import date_to_week
from interval.fields import IntervalField
from django.conf import settings
from tracks.providers import get_provider

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

  def get_path(self, name):
    return os.path.join(settings.GARMIN_DIR, self.user.username, '%s_%s.json' % (self.garmin_id, name))

  def get_data(self, name):
    src = self.get_path(name)
    if not os.path.exists(src):
      raise Exception('Invalid src %s' % src)
    with open(src, 'r') as f:
      return f.read()

  def to_track(self):
    '''
    Export to track
    '''
    # Check session does not already have a track
    if hasattr(self.session, 'track'):
      raise Exception('Session already has a track')

    # Load raw activity
    raw = json.loads(self.get_data('raw'))

    # Convert details to linestring
    provider = get_provider('garmin', self.user)
    provider.store_file(raw, 'details', self.get_data('details'))
    provider.store_file(raw, 'laps', self.get_data('laps'))
    line = LineString(provider.build_line_coords(raw))

    # Base track
    track = Track.objects.create(session=self.session, provider='garmin', provider_id=self.garmin_id, raw=line)
    track.simplify()
    track.save()

    # Add files
    for name in ('laps', 'details', 'raw'):
      path = self.get_path(name)
      if not os.path.exists(path):
        continue
      track.add_file(name, open(path, 'r').read())

    # Add splits
    distance_total, time_total = 0.0, 0.0
    for s in provider.build_splits(raw):
      s.track = track

      # Update totals
      distance_total += s.distance
      time_total += s.time
      s.distance_total = distance_total
      s.time_total = time_total

      s.save()

    return track, True
