from __future__ import absolute_import

from celery import shared_task

@shared_task
def tracks_import(*args, **kwargs):
  '''
  Import all new Tracks
  '''
  from users.models import Athlete
  for user in Athlete.objects.all():
    for provider in user.get_track_providers():
      provider.import_user()
