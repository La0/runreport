from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.conf import settings
from payments.account import RRAccount
from payments import get_api, get_notification_hash

from mangopaysdk.entities.hook import Hook

class Command(BaseCommand):

  def handle(self, *args, **kwargs):
    '''
    Setup mangopay RR wallet & account
    + notifications
    '''

    account = RRAccount()
    if account.Id:
      print('Using existing account %s and wallet %s' % (account.Id, account.wallet['Id']))
    else:
      print('Building account ...')
      account.build()

    notifications = (
      # Track payins
      'PAYIN_NORMAL_CREATED',
      'PAYIN_NORMAL_SUCCEEDED',
      'PAYIN_NORMAL_FAILED',
    )

    for n in notifications:
      try:
        self.add_notification(n)
      except Exception as e:
        print('Notif %s failure: %s' % (n, e))

  def add_notification(self, event_type):
    '''
    Create a notification on MangoPay
    for a specified type
    '''

    # Build url
    h = get_notification_hash(event_type)
    url = reverse('payment-notification', args=(h, ))
    url = settings.MANGOPAY_NOTIFICATION_URL + url
    print(' >> ', url)

    # Create notification
    hook = Hook()
    hook.Url = url
    hook.EventType = event_type

    api = get_api()
    resp = api.hooks.Create(hook)

    print(resp)
