from django.core.management.base import BaseCommand
from django.conf import settings
from payments.models import PaymentOffer
import paymill

class Command(BaseCommand):

  def handle(self, *args, **kwargs):
    '''
    Init paymill offers & hooks
    '''

    # Athlete offers
    self.build_offer('trimester', name='RR Trimestre', amount=14, currency='EUR', interval='3 MONTH')
    self.build_offer('yearly', name='RR Annuel', amount=35.0, currency='EUR', interval='1 YEAR')

    # Club offers
    self.build_offer('club', name='RR Club', amount=99.0, currency='EUR', interval='1 YEAR')

    event_types = [
      'subscription.created',
      'subscription.succeeded',
      'subscription.failed',
      'subscription.expiring',
      'subscription.deactivated',
      'subscription.activated',
      'subscription.canceled',
      'payment.expired',
    ]
    self.create_hook(event_types)

  def create_hook(self, event_types):
    '''
    Create a valid hook for the given event types
    Cleanup previous invalid hooks
    '''
    # List hooks
    ctx = paymill.PaymillContext(settings.PAYMILL_SECRET)
    webhook_service = ctx.get_webhook_service()
    hooks = webhook_service.list()

    # Check hooks
    valid = False
    for hook in hooks.data:
      # Only email hooks
      if 'email' not in hook:
        continue

      # Only consider hooks for current address
      if hook['email'] != settings.PAYMILL_HOOK_EMAIL:
        continue

      if hook['event_types'] == event_types and hook['active']:
        valid = True
        print 'Hook is still valid', hook
      else:
        # Cleanup old hooks
        from collections import namedtuple
        DummyHook = namedtuple('DummyHook', 'id')
        h = DummyHook(id=hook['id'])
        webhook_service.remove(h)

    # Create a new valid hook
    if not valid:
      hook = webhook_service.create_email(email=settings.PAYMILL_HOOK_EMAIL, active=True, event_types=event_types)
      print 'Created hook %s' % hook


  def build_offer(self, slug, paymill=True, **data):
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

