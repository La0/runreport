from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import paymill

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
  user = models.ForeignKey('users.Athlete', related_name='subscriptions')
  offer = models.ForeignKey('payments.PaymentOffer', related_name='subscriptions')

  # Status
  status = models.CharField(choices=SUBSCRIPTION_STATUS, max_length=20, default='created')

  # Paymill
  paymill_id = models.CharField(max_length=50, unique=True)

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (
      ('user', 'offer'),
    )

class PaymentOffer(models.Model):
  '''
  A payment offer & subscription
  through Paymill
  '''
  paymill_id = models.CharField(null=True, blank=True, max_length=50)
  slug = models.SlugField(unique=True, max_length=20)
  name = models.CharField(max_length=250)
  amount = models.FloatField()
  currency = models.CharField(max_length=10)
  interval = models.CharField(max_length=20)
  clients = models.ManyToManyField('users.Athlete', through=PaymentSubscription, related_name='offers')

  def __unicode__(self):
    return '%s : %f %s every %s' % (self.name, self.amount, self.currency, self.interval)

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

  def create_subscription(self, token, user):
    '''
    Create a payment for current offer
    with specified token from JS form
    and optional client
    Then link it to a subscription
    No db Item created here, only from hook
    '''
    if not user.paymill_id:
      raise Exception('Missing client paymill id')

    # Check there is not already a subscription for this user
    if self.subscriptions.filter(user=user).exists():
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

    # Create the subscription in Paymill
    ctx = paymill.PaymillContext(settings.PAYMILL_SECRET)
    service = ctx.get_subscription_service()
    subscription = service.create_with_offer_id(**data)

    # Save the subscription as awaiting validation
    user.subscriptions.create(offer=self, paymill_id=subscription.id)

    return subscription
