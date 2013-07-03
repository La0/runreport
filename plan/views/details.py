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

    return plan.get_absolute_url()

class PlanDetails(PlanMixin, DetailView):
  model = Plan
  template_name = 'plan/details.html'

  def get_context_data(self, *args, **kwargs):
    context = super(PlanDetails, self).get_context_data(*args, **kwargs)
    context['weeks'] = self.object.weeks.all().order_by('order')
    return context

  def post(self, request, *args, **kwargs):
    self.object = self.get_object()
    context = self.get_context_data(*args, **kwargs)
    print context

    # New week
    if request.POST['action'] == 'add-week': 
      PlanWeek.objects.create(plan=self.object, order=self.object.weeks.count())
    return self.render_to_response(context)

