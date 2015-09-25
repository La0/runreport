from __future__ import absolute_import

from celery import shared_task

@shared_task
def notify_message(message, user):
  '''
  Notify a user he has a new message
  by sending him an email
  '''
  from runreport.mail import MailBuilder

  builder = MailBuilder('mail/message.html', user.language)

  data = {
    'message' : message,
    'user' : user,
  }
  if message.conversation.type == 'comments_week':
    data['week'] = message.conversation.week
  builder.subject = u'[RunReport] Nouveau message'
  builder.to = [user.email, ]
  mail = builder.build(data)
  mail.send()
