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
from sport.views import RunCalendarYear, RunCalendar
from helpers import week_to_date

class AthleteCalendarYear(ProfilePrivacyMixin, RunCalendarYear):
  rights_needed = ('profile', 'calendar')

  def get_user(self):
    return self.member

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pageyear' : 'user-calendar-year',
      'pagemonth' : 'user-calendar-month',
      'pageday' : 'user-calendar-day',
    }

class AthleteCalendarMonth(ProfilePrivacyMixin, RunCalendar):
  rights_needed = ('profile', 'calendar')

  def get_user(self):
    return self.member

  def get_links(self):
    return {
      'pageargs' : [self.member.username, ],
      'pageyear' : 'user-calendar-year',
      'pagemonth' : 'user-calendar-month',
      'pageday' : 'user-calendar-day',
    }


class AthleteCalendarWeek(CurrentWeekMixin, ProfilePrivacyMixin, WeekPaginator, WeekArchiveView):
  rights_needed = ('profile', 'calendar')
  template_name = 'users/calendar/week.html'
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

class AthleteCalendarDay(ProfilePrivacyMixin, JsonResponseMixin, DateDetailView):
  rights_needed = ('profile', 'calendar')
  template_name = 'users/calendar/day.html'
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
