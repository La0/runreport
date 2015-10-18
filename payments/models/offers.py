from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import logging

logger = logging.getLogger('payments')

SUBSCRIPTION_STATUS = (
  ('created', _('Created')), # Awaiting validation
  ('active', _('Active')),
  ('inactive', _('Inactive')),
  ('expired', _('Expired')),
  ('failed', _('Failed')),
)

class PaymentSubscription(models.Model):
  '''
  A subscription between a club and an offer
  '''
  # Link to clubs
  club = models.ForeignKey('club.Club', related_name='subscriptions')

  # Max active Athletes
  nb_athletes = models.IntegerField(default=0)

  # Status
  status = models.CharField(choices=SUBSCRIPTION_STATUS, max_length=20, default='created')

  # Mangopay Id transaction
  mangopay_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  start = models.DateTimeField()
  end = models.DateTimeField()

  @property
  def remaining_days(self):
    '''
    Calc remaining days in subscription
    until end
    '''
    diff = self.end - timezone.now()
    return diff.days

  def cancel(self):
    '''
    Cancel the subscription through paymill
    '''
    raise Exception('Not implemented')

    # Check data
    if not self.paymill_id:
      raise Exception('Missing paymill id')
    if self.status not in ('active', 'created'):
      raise Exception('Invalid status')

    ctx = paymill.PaymillContext(settings.PAYMILL_SECRET)

    # Cancel subscription on Paymill
    service = ctx.get_subscription_service()
    sub = service.paymill_object()
    sub.id = self.paymill_id
    service.cancel(sub)

    # Refund part of transaction
    if self.remaining_days:
      remains = self.remaining_days / 365.0
      remains = min(remains, 0.75) # capped
    else:
      remains = 0.5
    service = ctx.get_refund_service()

    for t in self.club.transactions.filter(status='closed'):
      amount = t.amount * remains * 100
      service.refund_transaction(t.paymill_id, amount)

    # Kill the subscription
    self.status = 'inactive'
    self.end = timezone.now()
    self.save()
