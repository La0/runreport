from django.db import models
from django.utils.functional import cached_property
from datetime import datetime
from users.models import Athlete
import json

class PaymentEvent(models.Model):
  '''
  Represents an event sent from Paymill hooks
  '''
  event_id = models.CharField(max_length=32, unique=True)
  type = models.CharField(max_length=50)

  # Links
  user = models.ForeignKey('users.Athlete', null=True, blank=True, related_name='payment_events')
  subscription = models.ForeignKey('payments.PaymentSubscription', null=True, blank=True, related_name='events')
  transaction = models.ForeignKey('payments.PaymentTransaction', null=True, blank=True, related_name='events')

  # Raw event resource
  raw_data = models.TextField()

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  applied = models.DateTimeField(null=True, blank=True)

  def __unicode__(self):
    return '%s %s' % (self.type, self.event_id)

  @cached_property
  def data(self):
    return json.loads(self.raw_data)

  @cached_property
  def category(self):
    return self.type[:self.type.index('.')]

  def apply(self):
    '''
    Apply event to payment models
    '''
    from payments.models import PaymentTransaction, PaymentSubscription

    if self.applied:
      raise Exception('Event already applied')

    # Attach client
    if 'client' in self.data:
      try:
        self.user = Athlete.objects.get(paymill_id=self.data['client']['id'])
      except Athlete.DoesNotExist:
        pass
    if 'subscription' in self.data and not self.user:
      try:
        self.user = Athlete.objects.get(paymill_id=self.data['subscription']['client']['id'])
      except Athlete.DoesNotExist:
        pass

    ops = {
      'subscription.created' : self.__update_subscription,
      'subscription.succeeded' : self.__update_subscription,
      'transaction.created' : self.__update_transaction,
      'transaction.succeeded' : self.__update_transaction,
    }

    if self.type not in ops:
      raise Exception('Unsupported type operation %s' % self.type)
    out = ops[self.type]()

    # Link updated objects
    if isinstance(out, PaymentTransaction):
      self.transaction = out
    if isinstance(out, PaymentSubscription):
      self.subscription = out

    # Save application date
    self.applied = datetime.now()
    self.save()

  def __update_subscription(self):
    '''
    Create or update a Subscription
    '''
    from payments.models import PaymentOffer, PaymentSubscription
    sub_data = 'subscription' in self.data and self.data['subscription'] or self.data
    data = {
      'user' : self.user,
      'status' : sub_data['status'],
      'offer' : PaymentOffer.objects.get(paymill_id=sub_data['offer']['id']),
    }
    sub, created = PaymentSubscription.objects.get_or_create(paymill_id=sub_data['id'], defaults=data)
    if not created:
      for k,v in data.items():
        setattr(sub, k, v)
      sub.save()

    return sub

  def __update_transaction(self):
    '''
    Create or update a Transaction
    '''
    from payments.models import PaymentTransaction
    data = {
      'user' : self.user,
      'status' : self.data['status'],
      'amount' : float(self.data['amount']) / 100.0,
      'currency' : self.data['currency'],
    }
    transaction, created = PaymentTransaction.objects.get_or_create(paymill_id=self.data['id'], defaults=data)
    if not created:
      for k,v in data.items():
        setattr(transaction, k, v)
      transaction.save()

    return transaction

