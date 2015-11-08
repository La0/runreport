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
