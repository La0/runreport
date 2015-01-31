from __future__ import absolute_import

from celery import shared_task

@shared_task
def publish_plan(plan, users):
  '''
  Publish a plan to specified users
  '''
  plan.publish(users)
