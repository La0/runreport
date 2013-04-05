from datetime import timedelta

class WeekPaginator(object):
  weeks = []
  weeks_around_nb = 2

  # Build self.weeks for pagination
  def build_week(self, week_date, page_date):
    return {
      'display'  : 'week',
      'start' : week_date,
      'end'   : week_date + timedelta(days=6),
      'current' : (week_date == page_date),
      'week'  : week_date.strftime('%W'),
      'year'  : week_date.year,
    }

  def paginate(self, page_date, min_date, max_date):
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

