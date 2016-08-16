from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from payments.models import PaymentPeriod
from club.models import Club


class PaymentAthleteMixin(object):
  '''
  Checks the user is connected
  Adds helper to get periods
  '''
  no_active_periods = False
  club = None

  def dispatch(self, *args, **kwars):
    if not self.request.user.is_authenticated():
      raise PermissionDenied

    # Check no active periods are enabled
    subs = self.request.user.periods.all()
    if self.no_active_periods and subs.filter(offer__slug='athlete').exists():
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
    return self.request.user.periods.filter(status='active').exists()

class PaymentPeriodMixin(DetailView):
    """
    Mixin to retrieve a specific period
    for club managers & admins
    """
    def get_queryset(self):
        # Admin has full access
        user = self.request.user
        if user.is_staff:
            return PaymentPeriod.objects.all()

        # Limit to managed club periods
        return PaymentPeriod.objects.filter(club__manager=self.request.user)
