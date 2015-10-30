from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import logging

logger = logging.getLogger('payments')

SUBSCRIPTION_STATUS = (
  ('free', _('Free')), # Awaiting validation
  ('active', _('Active')),
  ('paid', _('Paid')),
  ('expired', _('Expired')),
  ('error', _('Error')),
)

class PaymentPeriod(models.Model):
  '''
  A subscription between a club and an offer
  '''
  # Link to clubs
  club = models.ForeignKey('club.Club', related_name='periods')

  # Max active roles
  nb_athletes = models.IntegerField(default=0)
  nb_trainers = models.IntegerField(default=0)
  nb_staff = models.IntegerField(default=0)

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

  @property
  def is_free(self):
    return self.status == 'free'

  def cancel(self):
    '''
    Cancel the subscription through paymill
    '''
    raise Exception('Not implemented')

  def pay(self, bill):
    '''
    Pay the subscription, automatically from task
    '''

    # Create payment on MangoPay
    try:
      logger.info('Create payment for %s (%f euros) - sub #%d' % (self.club, bill.total, self.pk))
      resp = self.club.init_payment(bill.total)

      if resp.Status == 'SUCCEEDED':
        # TODO: Send success mails
        # TODO: Update status
        pass
      else:
        raise Exception('Invalid response from Mangopay %s' % resp.Status)
    except Exception, e:
      logger.error('Payment failed for club %s : %s' % (self.club, e))

      # TODO: send manual payment mail
      # TODO: Update status

    # TODO: Send admin email
