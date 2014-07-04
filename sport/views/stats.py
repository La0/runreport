from django.views.generic import TemplateView
from datetime import date, timedelta
from sport.stats import StatsMonth
from calendar import monthrange
from sport.models import Sport, SportDay
from django.db.models import Min

class SportStats(TemplateView):
  template_name = 'sport/stats.html'

  def get_stats_months(self):
    '''
    Date boundaries for dataset
    By default, last 12 months
    '''
    today = date.today()

    # Get user from club or current
    try:
      user = self.member
    except AttributeError, e:
      user = self.request.user

    # List available years
    limits = SportDay.objects.filter(week__user=user).aggregate(min=Min('date'))
    years = reversed(range(limits['min'].year, today.year+1))

    year_delta = timedelta(days=365)
    if 'year' in self.kwargs:
      # Full Year
      year = int(self.kwargs['year'])
      start = date(year=year, month=1, day=1)
      end = start + year_delta
      date_range = 'year'

    elif 'all' in self.kwargs:
      # All the months !
      start = limits['min']
      end = today
      date_range = 'all'

    else:
      # Default: last 12 months
      end = today
      start = end - year_delta
      date_range = 'last'

    # Load the StatsMonths
    d = start
    months = []
    sports = []
    while d < end:
      stat = StatsMonth(user, d.year, d.month)
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
      'date_range' : date_range,
      'sports' : sports,
      'years' : years,
    }

  def get_url_context(self):
    # Gives user direct stats context
    return {
      'url_base' : 'stats',
      'url_month' : 'report-month',
      'url_args' : [],
    }

  def get_context_data(self, *args, **kwargs):
    context = super(SportStats, self).get_context_data(*args, **kwargs)
    context.update(self.get_stats_months())
    context.update(self.get_url_context())
    return context

