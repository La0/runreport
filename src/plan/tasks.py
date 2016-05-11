from __future__ import absolute_import

from celery import shared_task

@shared_task
def publish_plan(plan_pk, users_pk):
  '''
  Publish a plan to specified users
  '''
  from plan.models import Plan
  from users.models import Athlete
  plan = Plan.objects.get(pk=plan_pk)
  users = Athlete.objects.filter(pk__in=users_pk)
  plan.publish(users)

  return plan.pk # Avoid pickle issues

@shared_task
def athletes_daily_sessions():
  '''
  For all trainers, send a daily email
  with sessions about to be done today
  '''
  from django.utils.translation import ugettext_lazy as _
  from club.models import ClubMembership
  from sport.models import SportSession
  from runreport.mail import MailBuilder
  from datetime import date

  today = date.today()
  memberships = ClubMembership.objects.filter(role='trainer', user__daily_trainer_mail=True)
  for m in memberships:
    # List athletes sessions for today
    users = [cm.user for cm in m.athletes]
    sessions = SportSession.objects.filter(day__date=today, day__week__user__in=users)
    if not sessions:
      continue

    # Build mail
    mb = MailBuilder('mail/sessions.html', m.user.language)
    mb.to = [m.user.email, ]
    mb.subject = _('Your athlete\'s sessions today')
    context = {
      'club' : m.club,
      'user' : m.user,
      'sessions' : sessions,
    }
    mail = mb.build(context)
    mail.send()
