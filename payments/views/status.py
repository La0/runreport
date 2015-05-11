from .mixins import PaymentMixin
from django.views.generic import TemplateView


class PaymentStatus(PaymentMixin, TemplateView):
  '''
  Display payment status
  and premium membership data
  '''
  template_name = 'payments/status.html'
