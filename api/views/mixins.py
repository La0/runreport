from django.core.exceptions import PermissionDenied

class PlanMixin:
  '''
  Load a plan for api's views
  '''
  plan = None

  def load_plan(self):
    try:
      # Load plan
      self.plan = self.request.user.plans.get(pk=self.kwargs['pk'])
    except:
      raise PermissionDenied

    return self.plan
