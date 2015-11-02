from __future__ import absolute_import

from celery import shared_task

@shared_task
def auto_payments():
  '''
  Automatic payments
   * save max roles
   * auto payment on periodscription end
  '''
  from club.models import Club
  from datetime import date
  today = date.today()

  for club in Club.objects.all():

    # Calc all new roles
    period = club.save_roles()
    if period is None:
      continue

    # Auto pay
    if period.status == 'active' and period.end.date() <= today:
      period.pay()
