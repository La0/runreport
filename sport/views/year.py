from django.views.generic.dates import YearArchiveView
from sport.models import SportDay
from datetime import date, timedelta
from django.http import Http404
from collections import OrderedDict
import calendar

class RunCalendarYear(YearArchiveView):
  template_name = 'sport/calendar/year.html'
  date_field = 'date'
  model = SportDay

  def get_dated_items(self):
    year = int(self.get_year())

    # Get all days as datetimes
    # an ordered dict of
    # 12 months ordered dict
    # of datetimes, None
    cal = calendar.Calendar()
    months = OrderedDict([(date(year, m, 1), OrderedDict([
      (d, None) for d in cal.itermonthdates(year, m) if d.month == m
    ])) for m in range(1, 13)]) # yup.

    # Load SportDays + SportSession
    date_start = d = date(year, 1, 1)
    date_end = date(year, 12, 31)
    days_raw = SportDay.objects.filter(week__user=self.get_user(), date__gte=date_start, date__lte=date_end)
    days_raw = days_raw.prefetch_related('sessions', 'sessions__sport', 'sessions__plan_session')
    days_raw = days_raw.order_by('date')

    # Map days in months
    months_active = []
    for d in days_raw:
      months[date(year, d.date.month,1)][d.date] = d

      # List only month with active days
      # for small displays
      if d.date.month not in months_active:
        months_active.append(d.date.month)

    context = {
      'year' : year,
      'previous_year' : year-1,
      'next_year' : year+1,
      'member' : getattr(self, 'member', None),
      'months_active' : months_active,
    }
    context.update(self.get_links())

    return (months, days_raw, context)

  def get_user(self):
    return self.request.user

  def get_links(self):
    return {
      'pageargs' : [],
      'pageyear' : 'report-year',
      'pagemonth' : 'report-month',
      'pageday' : 'report-day',
    }
