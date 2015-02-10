from plan.models import Plan
from django.db.models import Q

class PlanMixin:
  context_object_name = 'plan'

  def get_queryset(self):
    '''
    Plans are available for:
     * its creator
     * the assigned athletes
    '''
    return Plan.objects.filter( \
      Q(creator=self.request.user) | \
      Q(sessions__applications__sport_session__day__week__user=self.request.user) \
    ).distinct()
