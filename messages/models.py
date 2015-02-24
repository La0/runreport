from django.db import models
from users.models import Athlete
from users.notification import UserNotifications
from django.core.urlresolvers import reverse
from messages.tasks import notify_message

TYPE_MAIL = 'mail'
TYPE_COMMENTS_PUBLIC = 'comments_public'
TYPE_COMMENTS_PRIVATE = 'comments_private'
TYPE_PLAN_SESSION = 'plan_session'

class Conversation(models.Model):
  CONVERSATION_TYPES = (
    (TYPE_MAIL, 'Mail'),
    (TYPE_COMMENTS_PUBLIC, 'Public comments'),
    (TYPE_COMMENTS_PRIVATE, 'Private comments'),
    (TYPE_PLAN_SESSION, 'Plan session'),
  )

  type = models.CharField(max_length=50, choices=CONVERSATION_TYPES)
  created = models.DateTimeField(auto_now_add=True)

  # Users markers, for filter / inbox
  mail_recipient = models.ForeignKey(Athlete, null=True, blank=True, related_name='mail_conversations')
  session_user = models.ForeignKey(Athlete, null=True, blank=True, related_name='session_conversations')

  def get_absolute_url(self):
    if self.type == TYPE_MAIL:
      return reverse('conversation-view', args=(self.pk, ))

    # View session
    session = self.get_session()
    dt = session.day.date
    return reverse('user-calendar-day', args=(session.day.week.user.username, dt.year, dt.month, dt.day))

  def get_session(self):
    if self.type == TYPE_MAIL:
      raise Exception("No session on conversation typed : %s" % self.type)

    # Check the session is attached
    name = self.type == TYPE_COMMENTS_PRIVATE and 'session_private' or 'session_public'
    if not hasattr(self, name):
      raise Exception('Missing session %s' % name)

    return getattr(self, name)

  def get_recipients(self, exclude=None):
    '''
    List all the recipients involved in a conversation
    Option: exclude a user not needed in a list
    '''
    writers = [m.writer for m in self.messages.exclude(writer=exclude).distinct('writer')]
    if self.type == TYPE_MAIL:
      # Send to all writers + mail recipient
      if self.mail_recipient and self.mail_recipient != exclude and self.mail_recipient not in writers:
        writers += [ self.mail_recipient, ]

      return writers

    elif self.type == TYPE_COMMENTS_PUBLIC:
      # Send to all writers + session user
      session = self.get_session()
      session_user = session.day.week.user
      if session_user != exclude and session_user not in writers:
        writers += [ session_user, ]

      return writers

    elif self.type == TYPE_COMMENTS_PRIVATE:
      # Send to all trainer + session user
      trainers = []
      session = self.get_session()
      session_user = session.day.week.user

      for m in session.day.week.user.memberships.all():
        for trainer in m.trainers.all():
          if exclude and trainer == exclude:
            continue
          trainers.append(trainer)

      if session_user != exclude and session_user not in trainers:
        trainers += [ session_user, ]

      return trainers

    return []

  def notify(self, message):
    '''
    Notify all recipients, without writer
    '''
    for r in self.get_recipients(exclude=message.writer):
      print ' >> Notify %s' % r.username

      # Direct notification
      un = UserNotifications(r)
      un.add_message(message)

      # Async send an email too
      notify_message.delay(message, r)


class Message(models.Model):
  conversation = models.ForeignKey(Conversation, related_name='messages', default=None)
  writer = models.ForeignKey(Athlete, related_name='messages_written', default=None)
  message = models.TextField()

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  # Simple incremental revision on edits
  revision = models.IntegerField(default=1)
