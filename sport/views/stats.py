from django.views.generic import TemplateView
from datetime import date, timedelta
from sport.stats import StatsMonth
from calendar import monthrange
from sport.models import Sport

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

    # Default
    end = date.today()
    start = end - timedelta(days=365)
    self.date_range = 'last'

    # Load the StatsMonths
    d = start
    months = []
    sports = []
    while d < end:
      stat = StatsMonth(self.request.user, d.year, d.month)
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
    }


  def get_context_data(self, *args, **kwargs):
    context = super(SportStats, self).get_context_data(*args, **kwargs)
    context.update(self.get_stats_months())
    return context

