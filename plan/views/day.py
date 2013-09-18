from django.views.generic import DetailView
from django.views.generic.edit import FormView
from mixins import PlanMixin
from plan.forms import PlanSessionForm
from plan.models import PlanSession
from coach.mixins import JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML

class PlanDay(JsonResponseMixin, PlanMixin, FormView):
  template_name = 'plan/day.html'
  form_class = PlanSessionForm

  def get_form(self, form_class, *args, **kwargs):
    '''
    Update or Create a day plan
    '''
    if self.plan_session is None:
      self.plan_session = PlanSession(week=self.plan_week, day=int(self.kwargs['day']))
    if self.request.method == 'POST':
      return form_class(self.request.POST, instance=self.plan_session)
    return form_class(instance=self.plan_session)

  def get_context_data(self, *args, **kwargs):
    context = super(PlanDay, self).get_context_data(*args, **kwargs)
    context['session'] = self.plan_session
    return context

  def form_valid(self, form):
    self.plan_session = form.save()
    self.json_options = [JSON_OPTION_BODY_RELOAD]
    return self.render_to_response({'session':self.plan_session, 'form':form, })
