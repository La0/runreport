from __future__ import absolute_import

from celery import shared_task

@shared_task
def tracks_import(*args, **kwargs):
  '''
  Import all new Tracks
  '''
  from users.models import Athlete
  from tracks.providers import all_providers

  for user in Athlete.objects.all():
    providers = [p for p in all_providers(user) if p.is_connected()]
    for provider in providers:
      provider.import_user()
