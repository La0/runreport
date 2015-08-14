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
  from coach.mail import MailBuilder

  for a in Athlete.objects.all():

    # List incoming races
    races = a.list_related_races()
    if not races:
      continue

    # Build and send email
    context = {
      'user' : a,
      'races' : races,
    }
    mb = MailBuilder('mail/related_races.html', a.language)
    mb.to = [a.email, ]
    mb.subject = _('New friends races')
    mail = mb.build(context)
    mail.send()

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
