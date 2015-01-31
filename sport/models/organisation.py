# coding=utf-8
from __future__ import absolute_import
from django.db import models
from django.db.models import Count
from users.models import Athlete
from datetime import datetime, date, time, timedelta
import xlwt
import tempfile
from coach.settings import REPORT_SEND_DAY, REPORT_SEND_TIME
from coach.mail import MailBuilder
from helpers import date_to_day, week_to_date
from . import SESSION_TYPES
from sport.stats import StatsMonth
from .sport import SportSession
from collections import OrderedDict

class SportWeek(models.Model):
  user = models.ForeignKey(Athlete, related_name='sportweek')
  year = models.IntegerField(default=2013)
  week = models.IntegerField(default=0)
  published = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  comment = models.TextField(null=True, blank=True)
  task = models.CharField(max_length=36, null=True, blank=True)

  class Meta:
    unique_together = (('user', 'year', 'week'),)
    db_table = 'sport_week'
    app_label = 'sport'

  def __unicode__(self):
    # Nice display name, used in templates too
    st, end = self.get_date_start(), self.get_date_end()
    if st.month == end.month:
      return u'%d-%d %s' % (st.day, end.day, end.strftime('%B %Y'))

    # Default to full description
    return u'%s - %s' % (st.strftime('%d %B %Y'), end.strftime('%d %B %Y'))

  def get_dates(self):
    # Days from monday to sunday
    return [self.get_date(day) for day in (1,2,3,4,5,6,0)]

  def get_days_per_date(self):
    sessions = OrderedDict()
    days = self.days.prefetch_related('sessions').prefetch_related('sessions__comments_public', 'sessions__comments_private')

    # Empty days by default
    for d in self.get_dates():
      sessions[d] = None

    # Use fully loaded days
    for d in days:
      sessions[d.date] = d

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
    return not self.published and today >= self.get_date_start()

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
    days = self.get_days_per_date()
    for day_date, day in days.items():
      ws.write(i, 0, formats.date_format(day_date, 'DATE_FORMAT'), style_date)
      content = []
      if not day:
        i += 1
        continue

      # Sessions listing
      for s in day.sessions.all().order_by('created'):
        if s.name:
          content.append('%s - %s :' % (s.sport.name, s.name,))
        if s.comment:
          content.append(s.comment)

      # Add week comment
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
      'days' : self.get_days_per_date(),
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


  def get_sports_stats(self):
    '''
    List all the cumulated time & distance
    per sport for this week
    '''
    stats = []
    sessions = SportSession.objects.filter(day__week=self)
    sports = set([s.sport for s in sessions])

    for sport in sports:
      t, d = 0.0, 0.0
      for s in sessions.filter(sport=sport):
        if s.time:
          t += s.time.total_seconds()
        if s.distance:
          d += s.distance
      stats.append((sport, t, d))

    # Add total
    stats.append((None, sum([s[1] for s in stats]), sum([s[2] for s in stats])))

    return stats

  def rebuild_cache(self):
    # Rebuild the stats cache
    st = StatsMonth(self.user, self.year, self.get_date_start().month, preload=False)
    st.build()


class SportDay(models.Model):
  week = models.ForeignKey('SportWeek', related_name='days')
  date = models.DateField()
  sports = models.ManyToManyField('Sport', through='SportSession')

  class Meta:
    unique_together = (('week', 'date'),)
    db_table = 'sport_day'
    app_label = 'sport'

  def sports_count(self):
    # List sports usage in this day
    counts = self.sports.all().values('pk').annotate(total=Count('pk')).order_by('total')
    return [(self.sports.filter(pk=c['pk']).first(), c['total']) for c in counts]

  def types_count(self):
    # List types usage in this day
    counts = self.sessions.values('type').annotate(total=Count('type')).order_by('total')
    return [(c['type'], c['total']) for c in counts]

  def best_type(self):
    # Gives the best type reprensenting day
    # Race > Training > Rest
    types = [t[0] for t in self.types_count()]
    for t in ('race', 'training', 'rest'):
      if t in types:
        return t
    return 'rest'

  def rebuild_cache(self):
    # Rebuild the stats cache
    st = StatsMonth(self.week.user, self.date.year, self.date.month, preload=False)
    st.build()

class RaceCategory(models.Model):
  name = models.CharField(max_length=250)
  distance = models.FloatField(null=True, blank=True)

  class Meta:
    db_table = 'sport_race_category'
    app_label = 'sport'

  def __unicode__(self):
    return self.name
