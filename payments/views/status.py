from .mixins import PaymentMixin
from payments.models import PaymentOffer
from coach.features import list_features
from django.views.generic import TemplateView


class PaymentStatus(PaymentMixin, TemplateView):
  '''
  Display payment status
  and premium membership data
  '''
  template_name = 'payments/status.html'

  def get_context_data(self, *args, **kwargs):
    context = super(PaymentStatus, self).get_context_data(*args, **kwargs)
    context['offers'] = {
      'trimester' : PaymentOffer.objects.get(slug='trimester'),
      'yearly' : PaymentOffer.objects.get(slug='yearly'),
    }
    context['subscriptions'] = self.request.user.subscriptions.all()
    context['transactions'] = self.request.user.payment_transactions.all()
    context.update(list_features(only_premium=True))
    return context
