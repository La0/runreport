from django.db import models
from django.conf import settings
import paymill

class PaymentSubscription(models.Model):
  '''
  A subscription between a user and an offer
  '''
  # M2M links
  user = models.ForeignKey('users.Athlete', related_name='subscriptions')
  offer = models.ForeignKey('payments.PaymentOffer', related_name='subscriptions')

  # Status
  active = models.BooleanField(default=False)

  # Paymill
  paymill_id = models.CharField(max_length=50)
  paymill_transaction_id = models.CharField(max_length=50)

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
    Create a transaction for current offer
    with specified token from JS form
    and optional client
    Then use link its payment to a subscription
    '''
    if not user.paymill_id:
      raise Exception('Missing client paymill id')

    # Check there is not already a subscription for this user
    if self.subscriptions.filter(user=user).count() > 0:
      raise Exception('Already a subscription for this offer & user')

    # Prepare data for transaction
    data = {
      'amount' : self.amount_cents,
      'currency' : self.currency,
      'description' : self.name,
      'client_id' : user.paymill_id,
      'token' : token,
    }

    # Create the transaction in Paymill
    ctx = paymill.PaymillContext(settings.PAYMILL_SECRET)
    service = ctx.get_transaction_service()
    transaction = service.create_with_token(**data)

    # Prepare data for subscription
    data = {
      'offer_id' : self.paymill_id,
      'payment_id' : transaction.payment.id,
      'client_id' : user.paymill_id,
      'name' : self.name,
    }

    # Create the subscription in Paymill
    ctx = paymill.PaymillContext(settings.PAYMILL_SECRET)
    service = ctx.get_subscription_service()
    subscription = service.create_with_offer_id(**data)

    # Save it in database
    data = {
      'user' : user,
      'paymill_id' : transaction.id,
      'paymill_transaction_id' : transaction.id,
      'active' : subscription.status == 'active',
    }
    return self.subscriptions.create(**data)
