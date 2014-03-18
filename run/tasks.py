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
  from run.garmin import GarminConnector
  users = Athlete.objects.filter(garmin_login__isnull=False, garmin_password__isnull=False)
  users = users.exclude(garmin_login='') # don't use empty logins
  for user in users:
    GarminConnector.import_user(user)
