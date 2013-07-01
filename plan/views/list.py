from django.views.generic import ListView
from plan.models import Plan
from mixins import PlanMixin
from django.db.models import Count

class PlanList(PlanMixin, ListView):
  model = Plan
  template_name = 'plan/list.html'
  context_object_name = 'plans'

  def get_queryset(self):
    plans = Plan.objects.filter(creator=self.request.user)
    plans = plans.annotate(nb_weeks=Count('weeks'))
    return plans
