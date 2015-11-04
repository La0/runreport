from django.views.generic import DetailView
from payments.models import PaymentPeriod
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class PaymentPeriodView(DetailView):
  '''
  Process payment for a specified period
  '''
  template_name = 'payments/period.html'
  context_object_name = 'period'

  def get_queryset(self):
    # Only erroneous period for manager
    periods = PaymentPeriod.objects.filter(club__manager=self.request.user)
    periods = periods.filter(status__in=('expired', 'error'))
    return periods

  def post(self, *args, **kwargs):
    # Process payment
    period = self.get_object()
    period.pay()

    return HttpResponseRedirect(reverse('club-manage', args=(period.club.slug, )))
