# coding=utf-8
from django.db import models
from users.models import Athlete
from datetime import datetime, date, time, timedelta
import xlwt
import os
import json
import hashlib
import tempfile
from coach.settings import REPORT_SEND_DAY, REPORT_SEND_TIME, GARMIN_DIR
from coach.mail import MailBuilder
from helpers import date_to_day, week_to_date
import logging
from django.utils.timezone import utc
from helpers import date_to_week

class RunReport(models.Model):
  user = models.ForeignKey(Athlete)
  year = models.IntegerField(default=2013)
  week = models.IntegerField(default=0)
  published = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  comment = models.TextField(null=True, blank=True)
  distance = models.FloatField(null=True, blank=True, editable=False)
  time = models.FloatField(null=True, blank=True, editable=False)
  task = models.CharField(max_length=36, null=True, blank=True)
  plan_week = models.ForeignKey('plan.PlanWeek', null=True, blank=True)

  class Meta:
    unique_together = (('user', 'year', 'week'),)

  def __unicode__(self):
    return u'%s : %d week=%d' % (self.user, self.year, self.week)

  def get_days(self):
    # Days from monday to sunday
    return [self.get_date(day) for day in (1,2,3,4,5,6,0)]

  def get_dated_sessions(self):
    sessions = {}
    for d in self.get_days():
      try:
        sessions[d] = self.sessions.get(date=d)
      except:
        sessions[d] = None
    return sessions

  def get_date(self, day):
    return week_to_date(self.year, self.week, day)

  def get_date_start(self):
    return self.get_date(1)

  def get_date_end(self):
    return self.get_date(0)

  def get_send_date(self):
    '''
    Build the next date to send reports
    '''
    day = self.get_date(REPORT_SEND_DAY)
    t = time(REPORT_SEND_TIME[0], REPORT_SEND_TIME[1])
    return datetime.combine(day, t)

  def is_current(self):
    today = date.today()
    return self.get_date_start() == date_to_day(today)

  def is_publiable(self):
    today = date.today()
    return not self.published and today >= self.get_date(0)

  @models.permalink
  def get_absolute_url(self):
    return ('report-week', [self.year, self.week])

  def build_xls(self):
    '''
    Build excel file using sessions
    '''
    from django.utils import formats

    font = xlwt.Font()
    font.bold = True

    align = xlwt.Alignment()
    align.wrap = 1 # Display line feeds
    style_align = xlwt.XFStyle()
    style_align.alignment = align

    style_date = xlwt.XFStyle()
    style_date.num_format_str = 'DD-MM-YYYY'
    style_date.font = font

    wb = xlwt.Workbook()
    ws = wb.add_sheet('%s - %s' % (self.get_date_start(), self.get_date_end()))

    # Add content to xls
    i = 0
    sessions = self.get_dated_sessions()
    for day in self.get_days():
      ws.write(i, 0, formats.date_format(day, 'DATE_FORMAT'), style_date)
      content = []
      sess = sessions[day]
      if not sess:
        i += 1
        continue
      if sess.name:
        content.append('%s :' % (sess.name,))
      if sess.comment:
        content.append(sess.comment)
      for activity in sess.garmin_activities.all():
        content.append('Garmin: %s - %s km en %s = %s min/km' % (activity.name, activity.distance, activity.time, activity.speed))
        content.append(activity.get_url())
      if i == 6 and self.comment:
        content.append('Bilan de la semaine :')
        content.append(self.comment)
      ws.write(i, 1, '\n'.join(content), style_align)
      i += 1
    ws.col(0).width = 4000 # Static width for dates

    # Output to tmp file
    _, path = tempfile.mkstemp(suffix='.xls')
    wb.save(path)
    return path

  def publish(self, membership, base_uri=None):
    '''
    Publish this report
    '''
    if self.published:
      raise Exception('This report is already published')

    # Build xls
    xls = open(self.build_xls(), 'r')
    xls_name = '%s_semaine_%d.xls' % (self.user.username, self.week+1)

    # Context for html
    context = {
      'week_human' : self.week + 1,
      'report': self,
      'club': membership.club,
      'sessions' : self.get_dated_sessions(),
      'base_uri' : base_uri,
    }

    # Build mail
    headers = {'Reply-To' : self.user.email,}

    mb = MailBuilder('mail/report.html')
    mb.subject = u'Séance de %s : du %s au %s' % (self.user, self.get_date_start(), self.get_date_end())
    mb.to = [m.email for m in membership.trainers.all()]
    mb.cc = [self.user.email]
    mail = mb.build(context, headers)

    # Attach Xls & send
    mail.attach(xls_name, xls.read(), 'application/vnd.ms-excel')
    mail.send()

    self.published = True
    self.save()

  def calc_distance_time(self):
    # Distance, through SQL Sum
    from django.db.models import Sum
    out = self.sessions.aggregate(total_distance=Sum('distance'))
    self.distance = out['total_distance']

    # Time
    time = timedelta()
    for s in self.sessions.filter(time__isnull=False):
      time += timedelta(hours=s.time.hour, minutes=s.time.minute, seconds=s.time.second)
    self.time = time.days * 86400 + time.seconds
    return (self.distance, self.time)


SESSION_TYPES = (
  ('training', 'Entrainement'),
  ('race', 'Course'),
  ('rest', 'Repos'),
)

SESSION_SPORTS = (
  ('running', 'Course à pied'),
  ('cycling', 'Vélo'),
  ('swimming', 'Natation'),
)

class RunSession(models.Model):
  report = models.ForeignKey('RunReport', related_name='sessions')
  date = models.DateField()
  name = models.CharField(max_length=255, null=True, blank=True)
  comment = models.TextField(null=True, blank=True)
  distance = models.FloatField(null=True, blank=True)
  time = models.TimeField(null=True, blank=True)
  type = models.CharField(max_length=12, default='training', choices=SESSION_TYPES)
  sport = models.CharField(choices=SESSION_SPORTS, max_length=20, default='running')
  plan_session = models.ForeignKey('plan.PlanSession', null=True, blank=True)
  race_category = models.ForeignKey('RaceCategory', null=True, blank=True)

  class Meta:
    unique_together = (('report', 'date'),)

  def save(self, *args, **kwargs):
    # No race category when we are not in race
    if self.type != 'race':
      self.race_category = None

    super(RunSession, self).save(*args, **kwargs)

class GarminActivity(models.Model):
  garmin_id = models.IntegerField(unique=True)
  session = models.ForeignKey(RunSession, related_name='garmin_activities')
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
    report,_ = RunReport.objects.get_or_create(user=self.user, year=year, week=week)
    self.session,_ = RunSession.objects.get_or_create(date=date, report=report)

    # Use title ?
    modified = False
    if not self.session.name and self.name not in ('Sans titre', 'Untitled'):
      self.session.name = self.name
      modified = True

    # Use running time ?
    if self.sport.get_category() == 'running':
      if not self.session.distance:
        self.session.distance = self.distance
        modified = True
      if not self.session.time:
        self.session.time = self.time
        modified = True

    # Update session
    if modified:
      self.session.save()

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

class RaceCategory(models.Model):
  name = models.CharField(max_length=250)
  distance = models.FloatField(null=True, blank=True)

  def __unicode__(self):
    return self.name

class Sport(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(unique=True)
  parent = models.ForeignKey('Sport', null=True)
  depth = models.IntegerField(default=0)

  def __unicode__(self):
    return self.name

  def get_category(self):
    # Always give a valid parent category
    if self.depth <= 1 or not self.parent:
      return self.slug
    return self.parent.get_category()
