from __future__ import absolute_import

from celery import shared_task

@shared_task
def build_demos(*args, **kwargs):
  '''
  Build demos days / sessions
  '''
  from users.management.commands.setup_demos import Command
  cmd = Command()
  cmd.handle()

