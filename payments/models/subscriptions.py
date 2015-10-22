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
