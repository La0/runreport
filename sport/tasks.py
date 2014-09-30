from __future__ import absolute_import

from celery import shared_task

@shared_task
def auto_publish_reports():
  '''
  Publish all reports for this week
  '''
  from datetime import date
  from sport.models import SportWeek
  from django.db.models import Count
  today = date.today()
  year, week = today.year, int(today.strftime('%W'))
  reports = SportWeek.objects.filter(year=year, week=week, published=False).order_by('user__username')
  reports = reports.filter(user__auto_send=True) # Auto send must be enabled per user
  for r in reports:

    # Skip empty report
    agg = r.days.aggregate(nb=Count('sessions'))
    if not agg['nb']:
      print 'No active sessions for report %s' % r
      continue

    # Publish
    for m in r.user.memberships.all():
      r.publish(m, 'https://runreport.fr') # TODO : use a config
    print 'Published %s' % r

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
