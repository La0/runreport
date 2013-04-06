from datetime import datetime, timedelta, date
from coach.settings import REPORT_START_DATE
from django.http import Http404
from helpers import week_to_date, date_to_day

class CurrentWeekMixin(object):
  '''
  Gives the current year & week or
  uses the one from kwargs (url)
  '''
  def get_year(self):
    year = datetime.now().year
    return int(self.kwargs.get('year', year))

  def get_week(self):
    week = datetime.now().strftime(self.week_format)
    return int(self.kwargs.get('week', week))

  def check_limits(self):
    # Load min & max date
    self.today = date.today()
    min_year, min_week = REPORT_START_DATE
    self.min_date = week_to_date(min_year, min_week)
    self.max_date = date_to_day(self.today)

    # Check we are not in past or future
    if self.date < self.min_date:
      raise Http404('Too old.')
    if self.date > self.today:
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

