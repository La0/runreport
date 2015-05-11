from django.db import models
from django.conf import settings
import paymill


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

  def __unicode__(self):
    return '%s : %f %s every %s' % (self.name, self.amount, self.currency, self.interval)

  def sync_paymill(self):
    '''
    Sync the offer on paymill
    '''
    if self.paymill_id:
      raise Exception('Already a paymill id')

    # Prepare data
    data = {
      'name' : self.name,
      'amount' : int(self.amount * 100), # in cents
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
