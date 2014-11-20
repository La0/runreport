# coding=utf-8
from __future__ import absolute_import

from celery import shared_task

@shared_task
def notify_friend_request(sender, recipient, accepted=False):
  '''
  Notify a user he has a new or accepted friend request
  by sending him an email
  '''
  from coach.mail import MailBuilder

  builder = MailBuilder('mail/friend.request.html')

  data = {
    'sender' : sender,
    'recipient' : recipient,
    'accepted' : accepted,
  }
  if accepted:
    builder.subject = u'[RunReport] Demande d\'ami acceptée'
    builder.to = [sender.email, ]
  else:
    builder.subject = u'[RunReport] Nouvelle demande d\'ami'
    builder.to = [recipient.email, ]

  mail = builder.build(data)
  mail.send()
