from .mixins import PaymentAthleteMixin
from payments.models import PaymentOffer
from runreport.features import list_features
from django.utils import timezone
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404


class PaymentStatus(PaymentAthleteMixin, TemplateView):
  '''
  Display payment status
  and premium membership data
  '''
  template_name = 'payments/status.html'

  def get_context_data(self, *args, **kwargs):
    context = super(PaymentStatus, self).get_context_data(*args, **kwargs)
    context['now'] = timezone.now()

    # Load athlete offer
    context['offer'] = get_object_or_404(PaymentOffer, slug='athlete')

    # Load subscriptions & transactions
    subs = self.request.user.subscriptions.all()
    context['subscriptions'] = dict([(s.offer.slug, s) for s in subs])
    context['transactions'] = self.request.user.payment_transactions.all()

    # Load premium features
    context.update(list_features(only_premium=True))
    return context
