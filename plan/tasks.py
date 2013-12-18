from __future__ import absolute_import

from celery import shared_task

@shared_task
def apply_plan(plan, start_date, users):
  '''
  Apply a plan to a list of users
   * Link weeks & sessions to their sessions
   * Send each user a mail
  '''
  plan.apply(start_date, users)

