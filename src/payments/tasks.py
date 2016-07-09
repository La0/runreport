from __future__ import absolute_import
from celery import shared_task

import logging
logger = logging.getLogger(__name__)

@shared_task
def auto_payments():
  '''
  Automatic payments
   * save max roles
   * auto payment on periodscription end
  '''
  from club.models import Club

  for club in Club.objects.all():

    # Update club current period
    period = club.update_period()
    logger.info('Updated period {}'.format(period))

    continue # dry run

    # Auto pay
    if period.need_payment():
      period.pay()

@shared_task
def notify_club(period):
  '''
  Notify a club manager
  about a payment status
  '''
  from runreport.mail import MailBuilder
  from django.utils.translation import ugettext_lazy as _

  # Build and send email
  user = period.club.manager
  context = {
    'period' : period,
    'user' : user,
  }
  mb = MailBuilder('mail/payment.period.html', user.language)
  mb.to = [user.email, ]
  if period.status == 'paid':
    mb.subject = _('Payment successful')
  else:
    mb.subject = _('Payment error')
  mail = mb.build(context)
  mail.send()

@shared_task
def notify_admin(period):
  '''
  Notify a admins
  about a payment status
  '''
  from runreport.mail import MailBuilder
  from django.conf import settings
  from django.utils.translation import ugettext_lazy as _

  # Build and send email
  context = {
    'period' : period,
  }
  mb = MailBuilder('mail/payment.admin.html')
  mb.to = [m for n,m in settings.ADMINS]
  mb.subject = _('New Payment')
  mail = mb.build(context)
  mail.send()
