from django.views.generic import DetailView
from payments.models import PaymentOffer
from datetime import date, timedelta
from helpers import week_to_date

class PaymentOfferPay(DetailView):
  context_object_name = 'offer'
  model = PaymentOffer
  template_name = 'payments/offer.pay.html'

  def get_context_data(self, *args, **kwargs):
    context = super(PaymentOfferPay, self).get_context_data(*args, **kwargs)

    # Add 12 years for form
    now = date.today()
    context['years'] = [now+timedelta(days=y*365) for y in range(0, 13)]

    # List all months
    first = week_to_date(now.year, 2)
    context['months'] = [first+timedelta(days=30*d) for d in range(0, 12)]

    return context
