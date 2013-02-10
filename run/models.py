# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import xlwt
import tempfile
from django.core.mail import EmailMessage
from django.contrib.sites.models import get_current_site

class RunReport(models.Model):
  user = models.ForeignKey(User)
  year = models.IntegerField(default=2013)
  week = models.IntegerField(default=0)
  published = models.BooleanField(default=False)

  class Meta:
    unique_together = (('user', 'year', 'week'),)

  def __unicode__(self):
    return u'%s : %d week=%d' % (self.user, self.year, self.week)

  def init_sessions(self):
    '''
    Build sessions for the current week
    '''
    for day in range(0,7):
      date = self.get_date(day)
      RunSession.objects.get_or_create(report=self, date=date)

  def get_date(self, day):
    return datetime.strptime('%d %d %d' % (self.year, self.week, day), '%Y %W %w').date()

  def get_date_start(self):
    return self.get_date(1)

  def get_date_end(self):
    return self.get_date(0)

  def build_xls(self):
    '''
    Build excel file using sessions
    '''
    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.colour_index = 2
    font.bold = True

    style_title = xlwt.XFStyle()
    style_title.font = font

    style_date = xlwt.XFStyle()
    style_date.num_format_str = 'DD-MM-YYYY'

    wb = xlwt.Workbook()
    ws = wb.add_sheet('%s - %s' % (self.get_date_start(), self.get_date_end()))

    i = 0
    for sess in self.sessions.all().order_by('date'):
      ws.write(i, 0, sess.date, style_date)
      ws.write(i, 1, sess.comment)
      i += 1

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
    xls_name = '%s_semaine_%d.xls' % (self.user.username, self.week)

    # Build & send message
    mail = EmailMessage(subject, message)
    mail.to = [profile.trainer.email]
    mail.cc = [self.user.email]
    mail.attach(xls_name, xls.read(), 'application/vnd.ms-excel')
    mail.send()

    self.published = True
    self.save()

class RunSession(models.Model):
  report = models.ForeignKey('RunReport', related_name='sessions')
  date = models.DateField()
  comment = models.TextField(null=True, blank=True)

  class Meta:
    unique_together = (('report', 'date'),)
