from __future__ import absolute_import

from celery import shared_task

@shared_task
def payments_hook():
  '''
  Track all Paymill events
  through mail hooks
  '''
  from payments.hook import PaymillHook
  ph = PaymillHook()
  ph.run()
