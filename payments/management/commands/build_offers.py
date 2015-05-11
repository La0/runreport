from django.core.management.base import BaseCommand
from payments.models import PaymentOffer

class Command(BaseCommand):

  def handle(self, *args, **kwargs):
    '''
    Init paymill offers
    '''
    self.build('monthly', name='RR Monthly', amount=3.5, currency='EUR', interval='1 MONTH')
    self.build('yearly', name='RR Yearly', amount=35.0, currency='EUR', interval='1 YEAR')

    # Init a special forced offer without a paymill id
    # for friends only
    self.build('friends', paymill=False, name='RR Friends', amount=0.0, currency='ponies', interval='forever')


  def build(self, slug, paymill=True, **data):
    offer,_ = PaymentOffer.objects.get_or_create(slug=slug, defaults=data)
    print offer
    if not paymill:
      print 'No paymill'
      return offer

    if offer.paymill_id:
      print 'Already sync %s' % offer.paymill_id
    else:
      offer.sync_paymill()
      print 'Sync OK'
    return offer

