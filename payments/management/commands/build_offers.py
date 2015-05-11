from django.core.management.base import BaseCommand
from payments.models import PaymentOffer

class Command(BaseCommand):

  def handle(self, *args, **kwargs):
    '''
    Init paymill offers
    '''
    self.build('monthly', name='RR Monthly', amount=3.5, currency='EUR', interval='1 MONTH')
    self.build('yearly', name='RR Yearly', amount=35.0, currency='EUR', interval='1 YEAR')

  def build(self, slug, **data):
    offer,_ = PaymentOffer.objects.get_or_create(slug=slug, defaults=data)
    print offer
    if offer.paymill_id:
      print 'Already sync %s' % offer.paymill_id
    else:
      offer.sync_paymill()
      print 'Sync OK'
    return offer

