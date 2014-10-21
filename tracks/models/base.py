from django.contrib.gis.db import models
from sport.models import SportSession, SportDay, SportWeek
from .file import TrackFile
from hashlib import md5
from helpers import date_to_week

class Track(models.Model):
  session = models.OneToOneField(SportSession, related_name='track')

  # Provider Source
  provider = models.CharField(max_length=50, default='manual')
  provider_id = models.CharField(max_length=50, null=True, blank=True)

  # PolyLines
  raw = models.LineStringField()
  simple = models.LineStringField(null=True, blank=True)
  objects = models.GeoManager()

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  # Local identity used to attach a session
  identity = {}

  class Meta:
    unique_together = (
      ('provider', 'provider_id'),
    )

  def simplify(self, tolerance=0.0001):
    '''
    Simplify the raw polyline
    '''
    self.simple = self.raw.simplify(tolerance)
    return self.simple

  def get_file(self, name):
    # Helper to access file by name
    try:
      return self.files.get(name=name)
    except:
      return None

  def add_file(self, name, data):
    if not self.pk:
      raise Exception("Can't add any file without a PK")

    # Calc data md5 & check if update/creation is needed
    h = md5(data).hexdigest()
    f = self.get_file(name)
    if f and f.md5 == h:
      return f

    # Create TrackFile
    if not f:
      f = TrackFile.objects.create(track=self, name=name, md5=h)

    # Store data
    f.set_data(data)

    return f

  def attach_session(self, user):
    # Chekc field
    fields = ('name', 'date', 'distance', 'sport', 'time')
    for f in fields:
      if f not in self.identity:
        raise Exception("Missing identity field %s" % f)

    # Attach Activity to valid session
    week, year = date_to_week(self.identity['date'])
    sport_week,_ = SportWeek.objects.get_or_create(user=user, year=year, week=week)
    day,_ = SportDay.objects.get_or_create(date=self.identity['date'], week=sport_week)

    # Search an existing session
    sessions = day.sessions.filter(sport=self.identity['sport'].get_parent(), track__isnull=True)
    min_ratio = None
    if sessions.count():
      # Sort by closest distance & time
      # using a rationalised diff for distance & time
      for s in sessions:
        ratio_time, ratio_distance = None, None
        if s.time and self.identity['time']:
          t = self.identity['time'].total_seconds()
          ratio_time = abs(s.time.total_seconds() - t) / t
        if s.distance and self.identity['distance']:
          ratio_distance = abs(s.distance - self.identity['distance']) / self.identity['distance']

        # Sum ratios with compensation for empty values
        ratio = (ratio_time or 0) + (ratio_distance or 0)
        if ratio_time is None or ratio_distance is None:
          ratio *= 2

        # Compare ratio to find best session
        if min_ratio is None or ratio < min_ratio:
          min_ratio = ratio
          self.session = s

        # Update title
        if self.identity['name'] and not self.session.name:
          self.session.name = self.identity['name']
          self.session.save()
    else:
      # Create new session
      self.session = SportSession.objects.create(sport=self.identity['sport'].get_parent(), day=day, time=self.identity['time'], distance=self.identity['distance'], name=self.identity['name'])

  def get_url(self):
    if self.provider == 'garmin':
      return 'http://connect.garmin.com/modern/activity/%s' % self.provider_id

    return None
