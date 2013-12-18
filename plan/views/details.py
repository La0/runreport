from django.views.generic import DetailView, View
from django.views.generic.edit import FormView, BaseUpdateView 
from django.http import HttpResponseRedirect
from mixins import PlanMixin, PlanUserMixin
from plan.forms import PlanCreationForm
from plan.models import Plan, PlanWeek
from coach.mixins import JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML

class PlanCreate(PlanMixin, FormView):
  template_name = 'plan/create.html'
  form_class = PlanCreationForm

  def get_form(self, form_class):
    if self.request.method == 'POST':
      return form_class(data=self.request.POST, creator=self.request.user)
    return form_class(creator=self.request.user)

  def form_valid(self, form):

    # Create plan
    plan = Plan.objects.create(creator=self.request.user, name=form.cleaned_data['name'])

    # Create weeks
    for w in range(0, int(form.cleaned_data['week'])):
      PlanWeek.objects.create(plan=plan, order=w)

    return HttpResponseRedirect(plan.get_absolute_url())

class PlanDetails(PlanMixin, DetailView):
  model = Plan
  template_name = 'plan/details.html'

  def get_context_data(self, *args, **kwargs):
    context = super(PlanDetails, self).get_context_data(*args, **kwargs)
    context['weeks'] = self.plan.weeks.all().order_by('order')
    return context

class PlanWeekDetails(PlanMixin, JsonResponseMixin, BaseUpdateView):
  json_options = [JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML]

  def post(self, request, *args, **kwargs):
    action = self.kwargs['action']
    if action == 'add': 
      # Cleanup week order
      cpt = 0
      for w in self.plan.weeks.all().order_by('order'):
        if w.order != cpt:
          w.order = cpt
          w.save()
        cpt += 1

      # New week
      PlanWeek.objects.create(plan=self.plan, order=cpt)

    elif action == 'delete':
      # Delete week
      self.plan.weeks.get(order=self.kwargs['week']).delete()

    else:
      raise Exception("Invalid action")

    return self.render_to_response({})

class PlanUserDetails(PlanUserMixin, DetailView):
  template_name = 'plan/user.html'
