from datetime import datetime, timedelta, date
from coach.settings import REPORT_START_DATE
from django.http import Http404
from helpers import week_to_date, date_to_day, date_to_week
from run.models import RunReport, RunSession, SESSION_TYPES

class CurrentWeekMixin(object):
  '''
  Gives the current year & week or
  uses the one from kwargs (url)
  '''
  _today = None
  _week = None
  _year = None

  def __init__(self):
    self._today = date.today()
    self._week, self._year = date_to_week(date.today())

  def get_year(self):
    return int(self.kwargs.get('year', self._year))

  def get_week(self):
    return int(self.kwargs.get('week', self._week))

  def check_limits(self):
    # Load min & max date
    min_year, min_week = REPORT_START_DATE
    self.min_date = week_to_date(min_year, min_week)
    self.max_date = date_to_day(self._today)

    # Check we are not in past or future
    if self.date < self.min_date:
      raise Http404('Too old.')
    if self.date > self._today:
      raise Http404('In the future.')


class WeekPaginator(object):
  '''
  Paginates using weeks urls around a date
  '''
  weeks = []
  weeks_around_nb = 2

  # Build self.weeks for pagination
  def build_week(self, week_date, page_date):
    return {
      'display'  : 'week',
      'start' : week_date,
      'end'   : week_date + timedelta(days=6),
      'current' : (week_date == page_date),
      'week'  : int(week_date.strftime('%W')),
      'year'  : week_date.year,
    }

  def paginate(self, page_date, min_date, max_date):
    self.weeks = []
    # Add first week
    self.weeks.append(self.build_week(min_date, page_date))

    # Add viewed week and X on each side
    weeks_around = range(-self.weeks_around_nb, self.weeks_around_nb+1)
    for i in weeks_around:
      dt = page_date + timedelta(days=i*7)
      if dt <= min_date or dt >= max_date:
        continue
      if i == min(weeks_around):
        self.weeks.append({'display' : 'spacer'})
      self.weeks.append(self.build_week(dt, page_date))
      if i == max(weeks_around):
        self.weeks.append({'display' : 'spacer'})

    # Add current week (last)
    self.weeks.append(self.build_week(max_date, page_date))

    # Search current
    current_pos = 0
    i = 0
    for w in self.weeks:
      if w['display'] == 'week' and w['start'] == page_date:
        current_pos = i
      i += 1

    week_previous = current_pos - 1 > 0 and self.weeks[current_pos - 1] or None
    week_next = current_pos + 1 < len(self.weeks) and self.weeks[current_pos + 1] or None

    # TODO: integrate to get_context_data
    return {
      'weeks' : self.weeks,
      'week_previous' : week_previous,
      'week_next' : week_next,
    }

class CalendarDay(object):
  '''
  Load a RunSession from a date in url
  '''
  month_format = '%M'
  context_object_name = 'session'

  def get_object(self):
    # Load day, report and eventual session
    self.day = date(int(self.get_year()), int(self.get_month()), int(self.get_day()))
    week, year = date_to_week(self.day)
    self.report, _ = RunReport.objects.get_or_create(user=self.request.user, year=year, week=week)
    try:
      self.object = RunSession.objects.get(report=self.report, date=self.day)
    except:
      self.object = RunSession(report=self.report, date=self.day)
    return self.object

  def get_context_data(self, **kwargs):
    context = super(CalendarDay, self).get_context_data(**kwargs)
    context['day'] = self.day
    context['report'] = self.report
    context['session_types'] = SESSION_TYPES
    return context

