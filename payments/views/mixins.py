from django.core.exceptions import PermissionDenied


class PaymentMixin(object):
  '''
  Checks the user is connected
  Adds helper to get subscriptions
  '''
  no_active_subscriptions = False

  def dispatch(self, *args, **kwars):
    if not self.request.user.is_authenticated():
      raise PermissionDenied

    # Check no active subscriptions are enabled
    if self.no_active_subscriptions and self.has_active_subscription():
      raise PermissionDenied

    return super(PaymentMixin, self).dispatch(*args, **kwars)

  def has_active_subscription(self):
    return self.request.user.subscriptions.filter(active=True).count() > 0
