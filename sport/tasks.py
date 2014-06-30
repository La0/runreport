from __future__ import absolute_import

from celery import shared_task

@shared_task
def publish_report(report, membership, uri):
  '''
  Publish a report: build mail with XLS, send it.
  '''
  report.publish(membership, uri)

@shared_task
def garmin_import(*args, **kwargs):
  '''
  Import all new Garmin Activities
  '''
  from users.models import Athlete
  from sport.garmin import GarminConnector
  users = Athlete.objects.filter(garmin_login__isnull=False, garmin_password__isnull=False)
  users = users.exclude(garmin_login='') # don't use empty logins
  for user in users:
    GarminConnector.import_user(user)

@shared_task
def race_mail(*args, **kwargs):
  '''
  Send a mail to all users having a race today
  '''
  from sport.models import SportDay
  from datetime import date, timedelta
  from coach.mail import MailBuilder

  # Setup mail builder
  builder = MailBuilder('mail/race.html')

  # Load tommorow's race
  tmrw = date.today() + timedelta(days=1)
  races = SportDay.objects.filter(date=tmrw, type='race')

  # Build and Send all mails
  for race in races:
    user = race.week.user
    data = {
      'race' : race,
      'user' : user,
    }
    builder.subject = u'Votre course %s - RunReport' % (race.name,)
    builder.to = [user.email, ]
    mail = builder.build(data)
    mail.send()
