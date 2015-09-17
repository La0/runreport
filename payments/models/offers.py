from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import datetime
import time
import paymill
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
  A subscription between a user and an offer
  '''
  # M2M links
  user = models.ForeignKey('users.Athlete', related_name='subscriptions', null=True, blank=True)
  club = models.ForeignKey('club.Club', related_name='subscriptions', null=True, blank=True)
  offer = models.ForeignKey('payments.PaymentOffer', related_name='subscriptions')

  # Status
  status = models.CharField(choices=SUBSCRIPTION_STATUS, max_length=20, default='created')

  # Paymill
  paymill_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  start = models.DateTimeField()
  end = models.DateTimeField(null=True, blank=True)

  class Meta:
    unique_together = (
      ('user', 'offer'),
      ('club', 'offer'),
    )

  @property
  def remaining_days(self):
    '''
    Calc remaining days in subscription
    until end
    '''
    if not self.end:
      return None

    diff = self.end - timezone.now()
    return diff.days

  def cancel(self):
    '''
    Cancel the subscription through paymill
    '''

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

    for t in self.user.transactions.filter(status='closed'):
      amount = t.amount * remains * 100
      service.refund_transaction(t.paymill_id, amount)

    # Kill the subscription
    self.status = 'inactive'
    self.end = timezone.now()
    self.save()


OFFERS_TARGET = (
  ('club', _('Club')),
  ('athlete', _('Athlete')),
)

class PaymentOffer(models.Model):
  '''
  A payment offer & subscription
  through Paymill
  '''
  paymill_id = models.CharField(null=True, blank=True, max_length=50)
  target = models.CharField(max_length=10, choices=OFFERS_TARGET, default='athlete')
  slug = models.SlugField(unique=True, max_length=20)
  name = models.CharField(max_length=250)
  amount = models.FloatField()
  currency = models.CharField(max_length=10)
  interval = models.CharField(max_length=20)
  clients = models.ManyToManyField('users.Athlete', through=PaymentSubscription, related_name='offers')
  clubs = models.ManyToManyField('club.Club', through=PaymentSubscription, related_name='offers')

  def __unicode__(self):
    return '%s : %f %s every %s' % (self.name, self.amount, self.currency, self.interval)

  def get_absolute_url(self, club=None):
    if club and self.target == 'club':
      return reverse('payment-offer-club', args=(self.slug, club.slug))
    return reverse('payment-offer', args=(self.slug, ))

  @property
  def amount_monthly(self):
    import re
    matches = re.match('(\d+) (MONTH|YEAR)', self.interval)
    if not matches:
      return 0

    nb = int(matches.group(1))
    factor = matches.group(2)
    if factor == 'MONTH' and nb > 0:
      return self.amount / nb
    if factor == 'YEAR':
      return self.amount / (12 * nb)
    return 0


  @property
  def amount_cents(self):
    # paymill needs amounts in cents
    return int(self.amount * 100)

  def sync_paymill(self):
    '''
    Sync the offer on paymill
    '''
    if self.paymill_id:
      raise Exception('Already a paymill id')

    # Prepare data
    data = {
      'name' : self.name,
      'amount' : self.amount_cents,
      'currency' : self.currency,
      'interval' : self.interval,
    }

    # Create the subscription
    ctx = paymill.PaymillContext(settings.PAYMILL_SECRET)
    service = ctx.get_offer_service()
    offer = service.create(**data)

    # Save the new paymill id
    self.paymill_id = str(offer['id'])
    self.save()

  def create_subscription(self, token, user, club=None):
    '''
    Create a payment for current offer
    with specified token from JS form
    and optional client
    Then link it to a subscription
    '''
    if not user.paymill_id:
      raise Exception('Missing client paymill id')

    # Check there is not already a subscription for this user
    if self.target == 'athlete' and self.subscriptions.filter(user=user).exists():
      raise Exception('Already a subscription for this offer & user')

    # Same check but for clubs
    if self.target == 'club':
      if not club:
        raise Exception('Missing club instance')
      if club.subscriptions.filter(user=user).exists():
        raise Exception('Already a subscription for this offer & user')

    # Prepare data for payment
    data = {
      'client_id' : user.paymill_id,
      'token' : token,
    }

    # Create the transaction in Paymill
    ctx = paymill.PaymillContext(settings.PAYMILL_SECRET)
    service = ctx.get_payment_service()
    payment = service.create(**data)

    # Prepare data for subscription
    data = {
      'offer_id' : self.paymill_id,
      'payment_id' : payment.id,
      'client_id' : user.paymill_id,
      'name' : self.name,
    }

    # Paymill subscription service
    ctx = paymill.PaymillContext(settings.PAYMILL_SECRET)
    service = ctx.get_subscription_service()

    if self.target == 'athlete':
      # Remaining free days ?
      try:
        sub = user.subscriptions.get(offer__slug='athlete_welcome', status='active')
        if not sub.end:
          raise Exception('Missing end date')
        start = sub.end # Paying subscription start at the end of welcome

      except PaymentSubscription.DoesNotExist:
        logger.warn('No welcome subscription for user %s' % user)
        start = datetime.now()
      data['start_at'] = time.mktime(start.timetuple())

      # Create the subscription in Paymill
      subscription = service.create_with_offer_id(**data)

      # Save the subscription as awaiting validation
      user.subscriptions.create(offer=self, paymill_id=subscription.id, start=start)

    if self.target == 'club' and club:
      # Create the subscription in Paymill
      subscription = service.create_with_offer_id(**data)

      # Save the subscription as awaiting validation
      start = datetime.now()
      club.subscriptions.create(offer=self, paymill_id=subscription.id, start=start)

    return subscription
