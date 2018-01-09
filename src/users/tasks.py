from __future__ import absolute_import

from celery import shared_task
from django.utils.translation import ugettext_lazy as _


@shared_task
def build_demos(*args, **kwargs):
    '''
    Build demos days / sessions
    '''
    from users.management.commands.setup_demos import Command
    cmd = Command()
    cmd.handle()


@shared_task
def send_related_races_mail():
    '''
    Send mails about incoming friends
    and club members races
    '''
    from users.models import Athlete
    from runreport.mail import MailBuilder

    for a in Athlete.objects.all():

        # List incoming races
        races = a.list_related_races()
        if not races:
            continue

        # Build and send email
        context = {
            'user': a,
            'races': races,
        }
        mb = MailBuilder('mail/related_races.html', a.language)
        mb.to = [a.email, ]
        mb.subject = _('New friends races')
        try:
            mail = mb.build(context)
            mail.send()
        except Exception as e:
            print('Mail for races failed: %s' % str(e))


@shared_task
def subscribe_mailing(user, mailing_name):
    '''
    Subscribe an user to a mailing list
    '''
    user.subscribe_mailing(mailing_name)


@shared_task
def unsubscribe_mailing(user, mailing_name):
    '''
    Unsubscribe an user to a mailing list
    '''
    user.unsubscribe_mailing(mailing_name)


@shared_task
def delete_user(user):
    '''
    Backup and delete a user
    '''
    user.backup()
    user.delete()


@shared_task
def update_ml_usage(user, old_email, new_email):
    '''
    Update Mailing list subscriptions
    for a user on:
     * 'all' mailing list
     * every club mailing list
     * every group mailing list
    '''

    # 'all'
    mailings = ['all']

    # Clubs
    mailings += list(
        user.memberships.filter(
            club__mailing_list__isnull=False).values_list(
            'club__mailing_list',
            flat=True))

    # Groups
    mailings += list(
        user.memberships.filter(
            groups__mailing_list__isnull=False).values_list(
            'groups__mailing_list',
            flat=True))

    for ml in mailings:
        user.unsubscribe_mailing(ml, old_email)
        user.subscribe_mailing(ml, new_email)
