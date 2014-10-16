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

  def attach_session(self):
    # Attach Activity to valid session
    date = self.date.date()
    week, year = date_to_week(date)
    sport_week,_ = SportWeek.objects.get_or_create(user=self.user, year=year, week=week)
    day,_ = SportDay.objects.get_or_create(date=date, week=sport_week)

    # Search an existing session
    sessions = day.sessions.filter(sport=self.sport.get_parent(), garmin_activity__isnull=True)
    min_ratio = None
    if sessions.count():
      # Sort by closest distance & time
      # using a rationalised diff for distance & time
      for s in sessions:
        ratio_time, ratio_distance = None, None
        if s.time and self.time:
          t = self.time.total_seconds()
          ratio_time = abs(s.time.total_seconds() - t) / t
        if s.distance and self.distance:
          ratio_distance = abs(s.distance - self.distance) / self.distance

        # Sum ratios with compensation for empty values
        ratio = (ratio_time or 0) + (ratio_distance or 0)
        if ratio_time is None or ratio_distance is None:
          ratio *= 2

        # Compare ratio to find best session
        if min_ratio is None or ratio < min_ratio:
          min_ratio = ratio
          self.session = s


        # Update title
        if self.name and not self.session.name:
          self.session.name = self.name
          self.session.save()
    else:
      # Create new session
      self.session = SportSession.objects.create(sport=self.sport.get_parent(), day=day, time=self.time, distance=self.distance, name=self.name)

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
    print h_file, h_db
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
    if False and 'sumMovingDuration' in data:
      self.time = timedelta(seconds=float(data['sumMovingDuration']['value']))
    elif 'sumDuration' in data:
      t = data['sumDuration']['minutesSeconds'].split(':')
      self.time = timedelta(minutes=float(t[0]), seconds=float(t[1]))
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
    skip_titles = ('Sans titre', 'No title', )
    name = data['activityName']['value']
    self.name = name not in skip_titles and name or ''

  def get_speed_kph(self):
    # Transform speed form min/km to km/h
    if not self.speed:
      return 0.0
    return 3600.0 / (self.speed.hour * 3600 + self.speed.minute * 60 + self.speed.second)


  def build_track(self):
    '''
    Build a geo track from saved lines
    '''
    # Check session
    if not self.session:
      raise Exception("A SportSession is needed to build a track")
    if hasattr(self.session, 'track'):
      raise Exception("The SportSession has already a track")

    # Load metrics/measurements from file
    data = self.get_data('details')
    key = 'com.garmin.activity.details.json.ActivityDetails'
    if key not in data:
      raise Exception("Unsupported format")
    base = data[key]
    if 'measurements' not in base:
      raise Exception("Missing measurements")
    if 'metrics' not in base:
      raise Exception("Missing metrics")

    # Search latitude / longitude positions in measurements
    measurements = dict([(m['key'], m['metricsIndex']) for m in base['measurements']])
    if 'directLatitude' not in measurements or 'directLongitude' not in measurements:
      raise Exception("Missing lat/lon measurements")

    # Build linestring from metrics
    coords = []
    for m in base['metrics']:
      if 'metrics' not in m:
        continue
      lat, lng = m['metrics'][measurements['directLatitude']], m['metrics'][measurements['directLongitude']]
      if lat == 0.0 and lng == 0.0:
        continue
      coords.append((lat, lng))

    from django.contrib.gis.geos import LineString
    line = LineString(coords)


    # Build Track
    from tracks.models import Track
    track = Track.objects.create(raw=line, session=self.session)
    track.simplify()
    track.save()

    return track
