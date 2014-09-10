from __future__ import absolute_import
import calendar # TO KILL

from django.http import Http404
from users.views.mixins import ProfilePrivacyMixin
from sport.models import SportWeek
from django.views.generic import MonthArchiveView, DateDetailView
from django.views.generic.dates import WeekArchiveView
from sport.views.mixins import CurrentWeekMixin, WeekPaginator
from sport.models import SportDay
from datetime import datetime, date
from coach.mixins import JsonResponseMixin
from sport.views import RunCalendarYear
from helpers import week_to_date

class AthleteCalendarYear(ProfilePrivacyMixin, RunCalendarYear):

  def get_user(self):
    return self.member

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pageyear' : 'user-calendar-year',
      'pagemonth' : 'user-calendar-month',
      'pageday' : 'user-calendar-day',
    }

#TODO: refactor as Year above
class AthleteCalendarMonth(ProfilePrivacyMixin, MonthArchiveView):
  template_name = 'sport/calendar/month.html'
  date_field = 'date'
  model = SportDay
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
    sessions = SportDay.objects.filter(week__user=self.member, date__in=self.days)
    sessions_per_days = dict((r.date, r) for r in sessions)

    context = {
      'months' : (self.get_previous_month(day), day, self.get_next_month(day)),
      'days' : self.days,
      'weeks' : self.weeks,
      'pageyear' : 'user-calendar-year',
      'pagemonth' : 'user-calendar-month',
      'pageday' : 'user-calendar-day',
      'pageargs' : [self.member.username],
    }
    return (self.days, sessions_per_days, context)

#TODO: refactor as Year above
class AthleteCalendarWeek(CurrentWeekMixin, ProfilePrivacyMixin, WeekPaginator, WeekArchiveView):
  template_name = 'club/member.week.html'
  context_object_name = 'sessions'

  def get_dated_items(self):

    # Load report & sessions
    year = self.get_year()
    week = self.get_week()
    try:
      report = SportWeek.objects.get(user=self.member, year=year, week=week)
      sessions = report.get_days_per_date()
      dates = report.get_dates()
    except:
      report = sessions = dates = None

    context = {
      'year' : year,
      'week' : week,
      'report' : report,
      'member' : self.member,
      'pagename' : 'user-calendar-week',
      'pageargs' : [self.member.username],
    }

    # Pagination
    self.date = week_to_date(year, week)
    self.check_limits()
    context.update(self.paginate(self.date, self.min_date, self.max_date))

    return (dates, sessions, context)

#TODO: refactor as Year above
class AthleteCalendarDay(ProfilePrivacyMixin, JsonResponseMixin, DateDetailView):
  template_name = 'club/day.html'
  month_format = '%M'
  context_object_name = 'session'

  def get_context_data(self, **kwargs):
    context = super(AthleteCalendarDay, self).get_context_data(**kwargs)
    context['day'] = self.day
    context['report'] = self.week
    return context

  def get_object(self):
    # Load day, report and eventual session
    self.day = date(int(self.get_year()), int(self.get_month()), int(self.get_day()))
    week = int(self.day.strftime('%W'))
    self.week, _ = SportWeek.objects.get_or_create(user=self.member, year=self.day.year, week=week)
    try:
      self.object = SportDay.objects.get(week=self.week, date=self.day)
    except:
      self.object = None
    return self.object
