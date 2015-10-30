from __future__ import absolute_import

from celery import shared_task

@shared_task
def auto_payments():
  '''
  Automatic payments
   * save max roles
   * auto payment on subscription end
  '''
  from club.models import Club
  from datetime import date
  today = date.today()

  for club in Club.objects.all():
    sub, bill = club.save_roles()
    if sub is None:
      continue
    print club, sub.end.date(), today
    if sub.end.date() == today:
      sub.pay(bill)
