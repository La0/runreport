from __future__ import absolute_import

from celery import shared_task, task
from celery.task.sets import subtask

@shared_task
def tracks_import(*args, **kwargs):
  '''
  Import all new Tracks
  '''
  from users.models import Athlete
  from tracks.providers import all_providers

  for user in Athlete.objects.all():
    for provider in all_providers(user):
      if not provider.is_connected():
        continue

      # Start a subtask per import
      subtask('tracks.tasks.provider_import').delay(provider)

@task
def provider_import(provider):
  # Helper to run a provider import
  provider.import_user()
