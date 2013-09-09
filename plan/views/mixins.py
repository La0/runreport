from django.core.exceptions import PermissionDenied
from plan.models import Plan
from django.http import Http404

class PlanMixin(object):
  """
  View mixin which verifies that:
    * check the logged in user is a club trainer
    * or an admin
  """
  def dispatch(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    # Load memberships:
    # * only the club where they train for trainers
    # * the admin club where he is a member
    members = request.user.memberships
    if not request.user.is_staff:
      members = members.filter(role="trainer")
    if not members:
      raise PermissionDenied
    self.clubs = [m.club for m in members.all()]

    # Load optional plan (using plan_id kwargs)
    self.plan = None
    if 'plan_id' in kwargs:
      try:
        self.plan = Plan.objects.get(pk=kwargs['plan_id'], creator=request.user)
      except Exception, e:
        print str(e)
        raise Http404('Plan not found')

    return super(PlanMixin, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(PlanMixin, self).get_context_data(**kwargs)
    context['clubs'] = self.clubs
    return context

  def get_object(self):
    return self.plan
