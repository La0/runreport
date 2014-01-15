from django.views.generic import TemplateView
from run.models import RunSession


class RacesView(TemplateView):
  template_name = 'users/races.html'

  def get_context_data(self):
    context = super(RacesView, self).get_context_data()


    context['races'] = self.get_races()

    return context

  def get_races(self):
    # List races
    races = RunSession.objects.filter(report__user=self.request.user, type='race')


    return races
