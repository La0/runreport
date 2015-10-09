from django.core.management.base import BaseCommand
from payments.account import RRAccount


class Command(BaseCommand):

  def handle(self, *args, **kwargs):
    '''
    Setup mangopay RR wallet & account
    '''

    account = RRAccount()
    if account.Id:
      print 'Using existing account %s and wallet %s' % (account.Id, account.wallet['Id'])
    else:
      print 'Building account ...'
      account.build()
