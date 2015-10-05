from __future__ import absolute_import

from celery import shared_task, task

import logging
logger = logging.getLogger('tracks.tasks')

@shared_task
def tracks_import(*args, **kwargs):
  '''
  Import all new Tracks
  '''
  from users.models import Athlete
  from tracks.providers import all_providers

  users = Athlete.objects.all()
  users = users.order_by('pk')
  for user in users:
    if not user.is_premium:
      continue
    for provider in all_providers(user):
      if not provider.is_connected() or provider.is_locked:
        continue

      # Start a subtask per import
      provider_import.subtask((provider, )).apply_async()

@task
def provider_import(provider):
  '''
  Run a task for one specific import
  between locks
  '''
  if provider.is_locked:
    logger.warning('Provider %s for %s is locked' % (provider.NAME, provider.user) )
    return

  # Lock this provider
  provider.lock()

  # Run the import
  provider.import_user()

  # Unlock this provider
  provider.unlock()
