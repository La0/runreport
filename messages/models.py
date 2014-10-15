from django.db import models
from users.models import Athlete
from sport.models import SportSession
from users.notification import UserNotifications

TYPE_MAIL = 'mail'
TYPE_COMMENTS_PUBLIC = 'comments_public'
TYPE_COMMENTS_PRIVATE = 'comments_private'

class Conversation(models.Model):
  CONVERSATION_TYPES = (
    (TYPE_MAIL, 'Mail'),
    (TYPE_COMMENTS_PUBLIC, 'Public comments'),
    (TYPE_COMMENTS_PRIVATE, 'Private comments'),
  )

  type = models.CharField(max_length=50, choices=CONVERSATION_TYPES)
  created = models.DateTimeField(auto_now_add=True)

  # Users markers, for filter / inbox
  mail_recipient = models.ForeignKey(Athlete, null=True, blank=True, related_name='mail_conversations')
  session_user = models.ForeignKey(Athlete, null=True, blank=True, related_name='session_conversations')

  def get_session(self):
    if self.type == TYPE_MAIL:
      raise Exception("No session on conversation typed : %s" % self.type)
    f = {
      self.type : self.pk,
    }
    return SportSession.objects.get(**f)

  def get_recipients(self, exclude=None):
    '''
    List all the recipients involved in a conversation
    Option: exclude a user not needed in a list
    '''
    writers = [m.writer for m in self.messages.exclude(writer=exclude).distinct('writer')]
    if self.type == TYPE_MAIL:
      # Send to all writers + mail recipient
      if self.mail_recipient and self.mail_recipient not in writers:
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
    for r in self.get_recipients(message.writer):
      print ' >> Nptify %s' % r.username
      un = UserNotifications(r)
      un.add_message(message)

class Message(models.Model):
  conversation = models.ForeignKey(Conversation, related_name='messages', default=None)
  writer = models.ForeignKey(Athlete, related_name='messages_written', default=None)
  message = models.TextField()

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  # Simple incremental revision on edits
  revision = models.IntegerField(default=1)
