from django.views.generic import TemplateView
from sport.views.mixins import AthleteRaces
from datetime import date

class RacesView(AthleteRaces, TemplateView):
  template_name = 'users/races.html'

  def get_context_data(self, *args, **kwargs):
    context = super(RacesView, self).get_context_data(*args, **kwargs)

    # Add url parameters to see reports
    context.update({
      'raceurl' : 'report-day',
      'raceargs' : [],
      'today' : date.today(),
    })
    return context
