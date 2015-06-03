from django.db import models
from django.utils.translation import ugettext_lazy as _

TRANSACTION_STATUS = (
  ('open', _('Open')),
  ('pending', _('Pending')),
  ('closed', _('Closed')),
  ('failed', _('Failed')),
  ('partial_refunded', _('Partial Refund')),
  ('refunded', _('Refunded')),
  ('preauthorize', _('Pre-Authorize')),
  ('chargeback', _('Chargeback')),
)


class PaymentTransaction(models.Model):
  '''
  Every payment made by an user for a subscription
  '''
  user = models.ForeignKey('users.Athlete', null=True, blank=True, related_name='payment_transactions')
  paymill_id = models.CharField(unique=True, null=True, blank=True, max_length=50)

  amount = models.FloatField()
  currency = models.CharField(max_length=10)

  status = models.CharField(choices=TRANSACTION_STATUS, max_length=20, default='open')

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

