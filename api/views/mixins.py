from django.core.exceptions import PermissionDenied

class PlanMixin:
  '''
  Load a plan for api's views
  '''
  plan = None

  def load_plan(self):
    try:
      # Load plan
      pk = self.kwargs.get('plan_pk', self.kwargs.get('pk'))
      self.plan = self.request.user.plans.get(pk=pk)
    except Exception, e:
      print e.message
      raise PermissionDenied

    return self.plan
