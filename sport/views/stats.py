from django.views.generic import TemplateView
from datetime import date, timedelta
from sport.stats import StatsMonth
from calendar import monthrange
from sport.models import Sport, SportDay
from django.db.models import Min

class SportStats(TemplateView):
  template_name = 'sport/stats.html'

  # Date boundaries type
  # * last : last 12 months (default)
  date_range = 'last'

  def get_stats_months(self):
    '''
    Date boundaries for dataset
    By default, last 12 months
    '''
    today = date.today()

    # List available years
    limits = SportDay.objects.filter(week__user=self.request.user).aggregate(min=Min('date'))
    years = reversed(range(limits['min'].year, today.year+1))

    year_delta = timedelta(days=365)
    if 'year' in self.kwargs:
      # Full Year
      year = int(self.kwargs['year'])
      start = date(year=year, month=1, day=1)
      end = start + year_delta
      self.date_range = 'year'

    else:
      # Default: last 12 months
      end = today
      start = end - year_delta
      self.date_range = 'last'

    # Load the StatsMonths
    d = start
    months = []
    sports = []
    while d < end:
      stat = StatsMonth(self.request.user, d.year, d.month)
      if stat.sports:
        sports += stat.sports.keys()
      months.append(stat)

      # Switch to next month
      _, nb_days = monthrange(d.year, d.month)
      d += timedelta(days=nb_days - d.day + 1)

    # Unique sports
    sports = Sport.objects.filter(pk__in=set(sports))

    return {
      'start' : start,
      'end' : end,
      'months' : months,
      'date_range' : self.date_range,
      'sports' : sports,
      'years' : years,
    }


  def get_context_data(self, *args, **kwargs):
    context = super(SportStats, self).get_context_data(*args, **kwargs)
    context.update(self.get_stats_months())
    return context

