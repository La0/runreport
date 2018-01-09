from plan.models import Plan, PlanApplied
from django.db.models import Q


class PlanMixin(object):
    context_object_name = 'plan'

    def get_context_data(self, *args, **kwargs):
        context = super(PlanMixin, self).get_context_data(*args, **kwargs)
        context.update(self.get_application())
        return context

    def get_application(self):
        '''
        Load plan application (if any)
        '''
        try:
            application = self.request.user.plans_applied.get(
                plan=self.get_object())
        except PlanApplied.DoesNotExist:
            application = None
        return {
            'application': application,
        }

    def get_queryset(self):
        '''
        Plans are available for:
         * its creator
         * the assigned athletes
        '''
        if not self.request.user.is_authenticated():
            return Plan.objects.none()
        return Plan.objects.filter(
            Q(creator=self.request.user) |
            Q(sessions__applications__sport_session__day__week__user=self.request.user)
        ).distinct()
