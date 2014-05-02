# coding=utf-8
from django.db import models
from .organisation import SportDay
from .sport import SportSession
from users.models import Athlete
from datetime import datetime, time
import os
import json
import hashlib
from coach.settings import GARMIN_DIR
import logging
from django.utils.timezone import utc
from helpers import date_to_week

class GarminActivity(models.Model):
  garmin_id = models.IntegerField(unique=True)
  session = models.ForeignKey(SportSession, related_name='garmin_activities')
  sport = models.ForeignKey('Sport')
  user = models.ForeignKey(Athlete)
  name = models.CharField(max_length=255)
  time = models.TimeField()
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

    super(GarminActivity, self).save(*args, **kwargs)

  def attach_session(self):
    # Attach Activity to valid session
    date = self.date.date()
    week, year = date_to_week(date)
    sport_week,_ = SportWeek.objects.get_or_create(user=self.user, year=year, week=week)
    day,_ = SportDay.objects.get_or_create(date=date, week=sport_week)
    self.session,_ = SportSession.objects.get_or_create(sport=self.sport.get_parent(), day=day)

  def get_url(self):
    return 'http://connect.garmin.com/activity/%s' % (self.garmin_id)

  def get_data_path(self, name):
    return os.path.join(GARMIN_DIR, self.user.username, '%s_%s.json' % (self.garmin_id, name))

  def set_data(self, name, data):
    # Check dir
    path = self.get_data_path(name)
    path_dir = os.path.dirname(path)
    if not os.path.isdir(path_dir):
      os.makedirs(path_dir)

    # Set md5
    data_json = json.dumps(data)
    h = hashlib.md5(data_json).hexdigest()
    setattr(self, 'md5_%s' % name, h)

    # Dump in file
    fd = open(path, 'w+')
    fd.write(json.dumps(data))
    fd.close()

  def get_data(self, name):
    path = self.get_data_path(name)
    if not os.path.exists(path):
      return None

    # Check md5 before giving data
    h_db = getattr(self, 'md5_%s' % name)
    if h_db is None:
      return None
    fd = open(self.get_data_path(name), 'r')
    data = fd.read()
    h_file = hashlib.md5(data).hexdigest()
    fd.close()
    if h_file != h_db:
      raise Exception("Invalid data file %s" % path)
    return json.loads(data)

  def update(self, data=None):
    '''
    Update data stored in db from a dict
    If no data is given, load from local json
    '''
    logger = logging.getLogger('coach.run.garmin')

    if data is None:
      data = self.get_data('raw')
    if data is None:
      raise Exception('Empty data for GarminActivity %s' % self)

    # Type of sport
    self.sport = Sport.objects.get(slug=data['activityType']['key'])
    logger.debug('Sport: %s' % self.sport)

    # Date
    t = int(data['beginTimestamp']['millis']) / 1000
    self.date = datetime.utcfromtimestamp(t).replace(tzinfo=utc)
    logger.debug('Date : %s' % self.date)

    # Time
    if 'sumMovingDuration' in data:
      t = float(data['sumMovingDuration']['value'])
      self.time = datetime.utcfromtimestamp(t).time()
    elif 'sumDuration' in data:
      t = data['sumDuration']['display']
      self.time = datetime.strptime(t, '%H:%M:%S').time()
    else:
      raise Exception('No duration found.')
    logger.debug('Time : %s' % self.time)

    # Distance in km
    distance = data['sumDistance']
    if distance['unitAbbr'] == 'm':
      self.distance =  float(distance['value']) / 1000.0
    else:
      self.distance =  float(distance['value'])
    logger.debug('Distance : %s km' % self.distance)

    # Speed
    self.speed = time(0,0,0)
    if 'weightedMeanMovingSpeed' in data:
      speed = data['weightedMeanMovingSpeed']

      if speed['unitAbbr'] == 'km/h' or (speed['uom'] == 'kph' and self.sport.get_category() != 'running'):
        # Transform km/h in min/km
        s = float(speed['value'])
        mpk = 60.0 / s
        hour = int(mpk / 60.0)
        minutes = int(mpk % 60.0)
        seconds = int((mpk - minutes) * 60.0)
        self.speed = time(hour, minutes, seconds)
      elif speed['unitAbbr'] == 'min/km':
        try:
          self.speed = datetime.strptime(speed['display'], '%M:%S').time()
        except:
          s = float(speed['value'])
          minutes = int(s)
          self.speed = time(0, minutes, int((s - minutes) * 60.0))
    logger.debug('Speed : %s' % self.speed)

    # update name
    self.name = data['activityName']['value']

  def get_speed_kph(self):
    # Transform speed form min/km to km/h
    if not self.speed:
      return 0.0
    return 3600.0 / (self.speed.hour * 3600 + self.speed.minute * 60 + self.speed.second)


