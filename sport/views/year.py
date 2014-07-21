from coach.settings  import REPORT_START_DATE
from django.views.generic.dates import YearArchiveView
from sport.models import SportDay
from datetime import date, timedelta
from django.http import Http404
import collections

class RunCalendarYear(YearArchiveView):
  template_name = 'sport/calendar/year.html'
  date_field = 'date'
  model = SportDay

  def get_dated_items(self):
    # Check year
    year_min, _ = REPORT_START_DATE
    year = int(self.get_year())
    if year < year_min:
      raise Http404('Too old');

    # Get all days as datetimes
    # TODO: maybe a beter way through calendar ?
    date_start = d = date(year, 1, 1)
    date_end = date(year, 12, 31)
    months = {}
    while d <= date_end:
      if d.month not in months:
        months[d.month] = []
      months[d.month].append(d)
      d += timedelta(days=1)

    # Load days
    days_raw = SportDay.objects.filter(week__user=self.get_user(), date__gte=date_start, date__lte=date_end)

    # Map days in dict
    days = dict([(s.date, s) for s in days_raw])
    days = collections.OrderedDict(sorted(days.items()))

    # List only month with active days
    # for small displays
    months_active = set([d.date.month for d in days_raw])

    context = {
      'year' : year,
      'previous_year' : year-1 >= year_min and year-1 or None,
      'next_year' : year+1,
      'member' : getattr(self, 'member', None),
      'months_active' : months_active,
    }
    context.update(self.get_links())

    return (months, days, context)

  def get_user(self):
    return self.request.user

  def get_links(self):
    return {
      'pageargs' : [],
      'pageyear' : 'report-year',
      'pagemonth' : 'report-month',
      'pageday' : 'report-day',
    }