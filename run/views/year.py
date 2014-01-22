from coach.settings  import REPORT_START_DATE
from django.views.generic.dates import YearArchiveView
from run.models import RunSession
from datetime import date, timedelta
from django.http import Http404

class RunCalendarYear(YearArchiveView):
  template_name = 'run/year.html'
  date_field = 'date'
  model = RunSession

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

    # Load sessions
    sessions_raw = RunSession.objects.filter(report__user=self.request.user, date__gte=date_start, date__lte=date_end)

    # Map sessions in dict
    sessions = dict([(s.date, s) for s in sessions_raw])

    context = {
      'year' : year,
      'previous_year' : year-1 >= year_min and year-1 or None,
      'next_year' : year+1,
    }

    return (months, sessions, context)
