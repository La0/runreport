from django.views.generic import TemplateView
from datetime import date, timedelta
from sport.stats import StatsMonth
from calendar import monthrange

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
    while d < end:
      months.append(StatsMonth(self.request.user, d.year, d.month))

      # Switch to next month
      _, nb_days = monthrange(d.year, d.month)
      d += timedelta(days=nb_days - d.day + 1)

    return {
      'start' : start,
      'end' : end,
      'months' : months,
      'date_range' : self.date_range,
    }


  def get_context_data(self, *args, **kwargs):
    context = super(SportStats, self).get_context_data(*args, **kwargs)
    context.update(self.get_stats_months())
    return context

