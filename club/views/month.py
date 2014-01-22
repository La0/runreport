from django.http import Http404
from mixins import ClubMixin
from run.models import RunReport
from django.views.generic import MonthArchiveView, DateDetailView
from run.models import RunSession
from datetime import datetime, date
import calendar
from coach.mixins import JsonResponseMixin

class ClubMemberMonth(ClubMixin, MonthArchiveView):
  template_name = 'run/month.html'
  date_field = 'date'
  model = RunSession
  context_object_name = 'sessions'
  allow_future = True
  allow_empty = True

  def get_year(self):
    year = datetime.now().year
    return int(self.kwargs.get('year', year))

  def get_month(self):
    month = datetime.now().month
    return int(self.kwargs.get('month', month))

  # Load all days & weeks for this month
  def load_calendar(self, year, month):
    cal = calendar.Calendar(calendar.MONDAY)
    self.days = [d for d in cal.itermonthdates(year, month)]
    self.weeks = cal.monthdatescalendar(year, month)

  def get_dated_items(self):
    year = self.get_year()
    month = self.get_month()
    day = datetime.strptime('%s %s 1' % (year, month), '%Y %m %d')
    try:
      self.load_calendar(year, month)
    except Exception, e:
      raise Http404(str(e))

    # Load all sessions for this month
    sessions = RunSession.objects.filter(report__user=self.member, date__in=self.days)
    sessions_per_days = dict((r.date, r) for r in sessions)

    context = {
      'months' : (self.get_previous_month(day), day, self.get_next_month(day)),
      'days' : self.days,
      'weeks' : self.weeks,
      'pageyear' : 'club-member-year',
      'pagemonth' : 'club-member-month',
      'pageday' : 'club-member-day',
      'pageargs' : [self.club.slug, self.member.username],
    }
    return (self.days, sessions_per_days, context)

class ClubMemberDay(JsonResponseMixin, ClubMixin, DateDetailView):
  template_name = 'club/day.html'
  month_format = '%M'
  context_object_name = 'session'

  def get_context_data(self, **kwargs):
    context = super(ClubMemberDay, self).get_context_data(**kwargs)
    context['day'] = self.day
    context['report'] = self.report
    return context

  def get_object(self):
    # Load day, report and eventual session
    self.day = date(int(self.get_year()), int(self.get_month()), int(self.get_day()))
    week = int(self.day.strftime('%W'))
    self.report, _ = RunReport.objects.get_or_create(user=self.member, year=self.day.year, week=week)
    try:
      self.object = RunSession.objects.get(report=self.report, date=self.day)
    except:
      self.object = None
    return self.object
