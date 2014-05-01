# coding=utf-8
from django.db import models
from users.models import Athlete
from datetime import datetime, date, time, timedelta
import xlwt
import tempfile
from coach.settings import REPORT_SEND_DAY, REPORT_SEND_TIME
from coach.mail import MailBuilder
from helpers import date_to_day, week_to_date

class SportWeek(models.Model):
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

# To be replaces by SportSession
SESSION_SPORTS = (
  ('running', 'Course à pied'),
  ('cycling', 'Vélo'),
  ('swimming', 'Natation'),
)

class SportDay(models.Model):
  report = models.ForeignKey('SportWeek', related_name='sessions')
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

    super(SportDay, self).save(*args, **kwargs)

class RaceCategory(models.Model):
  name = models.CharField(max_length=250)
  distance = models.FloatField(null=True, blank=True)

  def __unicode__(self):
    return self.name


