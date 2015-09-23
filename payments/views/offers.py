from django.views.generic import DetailView, DeleteView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from datetime import date, timedelta
from helpers import week_to_date
from payments.models import PaymentSubscription
from .mixins import PaymentOfferActionMixin


class PaymentOfferPay(PaymentOfferActionMixin, DetailView):
  template_name = 'payments/offer.pay.html'
  no_active_subscriptions = True


  def get_context_data(self, *args, **kwargs):
    context = super(PaymentOfferPay, self).get_context_data(*args, **kwargs)

    # Add 12 years for form
    now = date.today()
    context['years'] = [now+timedelta(days=y*365) for y in range(0, 13)]

    # List all months
    first = week_to_date(now.year, 2)
    context['months'] = [first+timedelta(days=30*d) for d in range(0, 12)]

    return context

class PaymentOfferCancel(PaymentOfferActionMixin, DeleteView):
  template_name = 'payments/offer.cancel.html'

  def delete(self, *args, **kwargs):
    '''
    Cancel subscription
    Do a refund on paymill
    '''
    # Retrieve subscription
    offer = self.get_object()
    try:
      subscription = self.request.user.subscriptions.get(offer=offer, status__in=('active', 'created'))
    except PaymentSubscription.DoesNotExist:
      raise PermissionDenied

    # Kill it :(
    subscription.cancel()

    return HttpResponseRedirect(reverse('payment-status'))
