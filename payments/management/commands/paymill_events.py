from django.core.management.base import BaseCommand
from payments.hook import PaymillHook

class Command(BaseCommand):

  def handle(self, *args, **kwargs):
    '''
    Run Paymill hook once
    Mainly for dev purposes
    '''

    ph = PaymillHook()
    ph.run()
