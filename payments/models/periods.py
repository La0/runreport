from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from payments.bill import Bill
import logging

logger = logging.getLogger('payments')

PERIOD_STATUS = (
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
  status = models.CharField(choices=PERIOD_STATUS, max_length=20, default='active')

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

  @property
  def bill(self):
    '''
    Configure bill with saved data on period
    '''
    bill = Bill()
    bill.counts.update({
      'athlete' : self.nb_athletes,
      'staff' : self.nb_staff,
      'trainer' : self.nb_trainers,
    })
    bill.calc()
    return bill

  def pay(self):
    '''
    Pay the subscription, automatically from task
    '''

    # Create payment on MangoPay
    try:
      if not self.club.has_valid_card:
        raise Exception('Missing valid card')

      bill = self.bill
      logger.info('Create payment for %s (%f euros) - sub #%d' % (self.club, bill.total, self.pk))
      resp = self.club.init_payment(bill.total)

      if resp.Status == 'SUCCEEDED':
        # TODO: Send success mails
        # TODO: Update status
        self.status = 'paid'
        pass
      else:
        raise Exception('Invalid response from Mangopay %s' % resp.Status)
    except Exception, e:
      logger.error('Payment failed for club %s : %s' % (self.club, e))

      # TODO: send manual payment mail
      # TODO: Update status
      self.status = 'error'

    # Save new status
    self.save()

    # TODO: Send admin email
