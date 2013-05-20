# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, time, timedelta
import xlwt
import os
import json
import hashlib
import tempfile
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import get_current_site
from coach.settings import REPORT_SEND_DAY, REPORT_SEND_TIME, GARMIN_DIR
from helpers import date_to_day, week_to_date

class RunReport(models.Model):
  user = models.ForeignKey(User)
  year = models.IntegerField(default=2013)
  week = models.IntegerField(default=0)
  published = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  comment = models.TextField(null=True, blank=True)
  distance = models.FloatField(null=True, blank=True, editable=False)
  time = models.TimeField(null=True, blank=True, editable=False)

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
      activity = sess.garmin_activity
      if activity is not None:
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

  def publish(self):
    '''
    Publish this report
    '''
    if self.published:
      raise Exception('This report is already published')

    # Build corpus
    site = get_current_site(None)
    subject = u'Séance de %s : du %s au %s' % (self.user, self.get_date_start(), self.get_date_end())
    message = u'Envoyé via %s' % site
    profile = self.user.get_profile()
    xls = open(self.build_xls(), 'r')
    xls_name = '%s_semaine_%d.xls' % (self.user.username, self.week+1)

    # Render html version
    from coffin.shortcuts import render_to_string
    context = {
      'week_human' : self.week + 1,
      'report': self,
      'site': site,
      'sessions' : self.get_dated_sessions(),
    }
    mail_html = render_to_string('run/mail.html', context)

    # Build & send message
    headers = {'Reply-To' : self.user.email,}
    mail = EmailMultiAlternatives(subject, message, headers=headers)
    mail.to = [profile.trainer.email]
    mail.cc = [self.user.email]
    mail.attach_alternative(mail_html, 'text/html')
    mail.attach(xls_name, xls.read(), 'application/vnd.ms-excel')
    mail.send()

    self.published = True
    self.save()

  def calc_distance_time(self):
    # Distance, through SQL Sum
    from django.db.models import Sum
    out = self.sessions.aggregate(total_distance=Sum('distance'))
    self.distance = out['total_distance']

    # Time, not possible with django through sum...
    self.time = timedelta()
    for s in self.sessions.all():
      self.time += timedelta(hours=s.time.hour, minutes=s.time.minute, seconds=s.time.second)
    return (self.distance, self.time)

class RunSession(models.Model):
  report = models.ForeignKey('RunReport', related_name='sessions')
  date = models.DateField()
  name = models.CharField(max_length=255, null=True, blank=True)
  comment = models.TextField(null=True, blank=True)
  garmin_activity = models.ForeignKey('GarminActivity', null=True, blank=True)
  distance = models.FloatField(null=True, blank=True)
  time = models.TimeField(null=True, blank=True)

  class Meta:
    unique_together = (('report', 'date'),)

class GarminActivity(models.Model):
  garmin_id = models.IntegerField(unique=True)
  user = models.ForeignKey(User)
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
