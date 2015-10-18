from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from club.models import Club


class PaymentAthleteMixin(object):
  '''
  Checks the user is connected
  Adds helper to get subscriptions
  '''
  no_active_subscriptions = False
  club = None

  def dispatch(self, *args, **kwars):
    if not self.request.user.is_authenticated():
      raise PermissionDenied

    # Check no active subscriptions are enabled
    subs = self.request.user.subscriptions.all()
    if self.no_active_subscriptions and subs.filter(offer__slug='athlete').exists():
      raise PermissionDenied

    # Load club when specified
    if 'club_slug' in self.kwargs:
      self.club = get_object_or_404(Club, slug=self.kwargs['club_slug'], manager=self.request.user)

    return super(PaymentAthleteMixin, self).dispatch(*args, **kwars)

  def get_context_data(self, *args, **kwargs):
    context = super(PaymentAthleteMixin, self).get_context_data(*args, **kwargs)
    context['club'] = self.club
    return context

  def has_active_subscription(self):
    return self.request.user.subscriptions.filter(status='active').exists()
