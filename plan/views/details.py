from django.views.generic import DetailView
from .mixins import PlanMixin

class PlanDetails(PlanMixin, DetailView):
  template_name = 'plan/details.html'

  def get_context_data(self, *args, **kwargs):
    context = super(PlanDetails, self).get_context_data(*args, **kwargs)
    context.update(self.load_weeks())
    return context

  def load_weeks(self):
    '''
    Load weeks & sessions as a calendar
    '''
    weeks = [ [[] for d in range(0,7)] for i in range(0, self.object.get_weeks_nb())]
    for session in self.object.sessions.all():
      weeks[session.week][session.day].append(session)

    return {
      'weeks' : weeks,
    }
