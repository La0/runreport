from django.views.generic import DetailView
from django.views.generic.edit import DeleteView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .mixins import PlanMixin
from coach.mixins import JsonResponseMixin
from users.notification import UserNotifications

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

class PlanApplicationDelete(JsonResponseMixin, PlanMixin, DeleteView):
  template_name = 'plan/delete.html'

  def delete(self, *args, **kwargs):

    app = self.get_application()['application']

    # Notify creator the athlete has removed the plan
    un = UserNotifications(app.plan.creator)
    un.add_plan_application_removed(app)

    # Delete the application, not the plan !
    app.delete()

    return HttpResponseRedirect(reverse('report-current-month'))
