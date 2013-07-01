from django.views.generic import DetailView
from django.views.generic.edit import FormView
from mixins import PlanMixin
from plan.forms import PlanCreationForm
from plan.models import Plan, PlanWeek

class PlanCreate(PlanMixin, FormView):
  template_name = 'plan/create.html'
  form_class = PlanCreationForm

  def form_valid(self, form):

    # Create plan
    plan = Plan(creator=self.request.user, name=form.cleaned_data['name'])
    plan.start = form.cleaned_data['start']
    plan.save()

    # Create weeks
    for w in range(0, int(form.cleaned_data['week'])):
      PlanWeek.objects.create(plan=plan, order=w)

class PlanDetails(PlanMixin, DetailView):
  model = Plan
  template_name = 'plan/details.html'
