from __future__ import absolute_import
from celery import shared_task
from django.core.mail import mail_admins

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
    from django.db.models import Count
    from django.conf import settings

    report = []
    clubs = Club.objects.annotate(nb=Count('members'))
    clubs = clubs.order_by('-nb')
    for club in clubs:

        # Update club current period
        period = club.update_period()
        logger.info('Updated period {}'.format(period))
        report += ['Club #{} {} - {} members - '.format(
            club.pk, club.name, club.nb), str(period)]

        if period.need_payment():
            if settings.PAYMENTS_AUTO:
                period.pay()
                report += [' > AUTO PAID !']
            else:
                report += [' > SKIPPED AUTO PAYMENT, CHECK MANUALLY.']
        else:
            report += [' > no payment']

    # Send full report to admins
    mail_admins('RunReport Auto payments', '\n'.join(report))


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
        'period': period,
        'user': user,
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
        'period': period,
    }
    mb = MailBuilder('mail/payment.admin.html')
    mb.to = [m for n, m in settings.ADMINS]
    mb.subject = _('New Payment')
    mail = mb.build(context)
    mail.send()
