from django.views.generic import TemplateView
from sport.views.mixins import AthleteRaces

class RacesView(AthleteRaces, TemplateView):
  template_name = 'users/races.html'

  def get_context_data(self, *args, **kwargs):
    context = super(RacesView, self).get_context_data(*args, **kwargs)

    # Add url parameters to see reports
    context.update({
      'raceurl' : 'report-day',
      'raceargs' : [],
    })
    return context
