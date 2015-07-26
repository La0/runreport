from django.core.exceptions import PermissionDenied


class PaymentAthleteMixin(object):
  '''
  Checks the user is connected
  Adds helper to get subscriptions
  '''
  no_active_subscriptions = False

  def dispatch(self, *args, **kwars):
    if not self.request.user.is_authenticated():
      raise PermissionDenied

    # Check no active subscriptions are enabled
    subs = self.request.user.subscriptions.all()
    if self.no_active_subscriptions and subs.filter(offer__slug='athlete').exists():
      raise PermissionDenied

    return super(PaymentAthleteMixin, self).dispatch(*args, **kwars)

  def has_active_subscription(self):
    return self.request.user.subscriptions.filter(status='active').exists()
