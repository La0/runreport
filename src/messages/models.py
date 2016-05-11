from django.db import models
from users.models import Athlete
from users.notification import UserNotifications
from django.core.urlresolvers import reverse
from messages.tasks import notify_message

TYPE_MAIL = 'mail'
TYPE_COMMENTS_PUBLIC = 'comments_public'
TYPE_COMMENTS_PRIVATE = 'comments_private'
TYPE_COMMENTS_WEEK = 'comments_week'
TYPE_PLAN_SESSION = 'plan_session'
TYPE_POST = 'post'

class Conversation(models.Model):
  CONVERSATION_TYPES = (
    (TYPE_MAIL, 'Mail'),
    (TYPE_COMMENTS_PUBLIC, 'Public comments'),
    (TYPE_COMMENTS_PRIVATE, 'Private comments'),
    (TYPE_COMMENTS_WEEK, 'Week comments'),
    (TYPE_PLAN_SESSION, 'Plan session'),
    (TYPE_POST, 'Post'),
  )

  type = models.CharField(max_length=50, choices=CONVERSATION_TYPES)
  created = models.DateTimeField(auto_now_add=True)

  # Users markers, for filter / inbox
  mail_recipient = models.ForeignKey(Athlete, null=True, blank=True, related_name='mail_conversations')
  session_user = models.ForeignKey(Athlete, null=True, blank=True, related_name='session_conversations')

  def get_absolute_url(self):
    if self.type == TYPE_MAIL:
      return reverse('conversation-view', args=(self.pk, ))

    if self.type == TYPE_COMMENTS_WEEK:
      return reverse('user-calendar-week', args=(self.week.user.username, self.week.year, self.week.week))

    if self.type == TYPE_POST:
      return reverse('post', args=(self.post.writer.username, self.post.slug, ))

    # View session
    session = self.get_session()
    if not session:
      return reverse('conversation-view', args=(self.pk, ))
    dt = session.day.date
    return reverse('user-calendar-day', args=(session.day.week.user.username, dt.year, dt.month, dt.day))

  def get_session(self):
    if self.type not in (TYPE_COMMENTS_PRIVATE, TYPE_COMMENTS_PUBLIC, ):
      raise Exception("No session on conversation typed : %s" % self.type)

    # Check the session is attached
    name = self.type == TYPE_COMMENTS_PRIVATE and 'session_private' or 'session_public'
    if not hasattr(self, name):
      return None

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

    elif self.type == TYPE_POST:
      # Send to all writers + post writer
      if self.post.writer != exclude and self.post.writer not in writers:
        writers += [ self.post.writer, ]

      return writers

    elif self.type == TYPE_COMMENTS_PUBLIC:
      # Send to all writers + session user
      session = self.get_session()
      if not session:
        return []

      session_user = session.day.week.user
      if session_user != exclude and session_user not in writers:
        writers += [ session_user, ]

      return writers

    elif self.type in (TYPE_COMMENTS_PRIVATE, TYPE_COMMENTS_WEEK, ):
      # Send to all trainer + session user
      trainers = []
      if self.type == TYPE_COMMENTS_PRIVATE:
        session = self.get_session()
        if not session:
          return []
        user = session.day.week.user
      else:
        user = self.week.user

      for m in user.memberships.all():
        for trainer in m.trainers.all():
          if exclude and trainer == exclude:
            continue
          trainers.append(trainer)

      if user != exclude and user not in trainers:
        trainers += [ user, ]

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

  def copy(self, conversation):
    '''
    Copy a message to another conversation
    Do not add if same message alredy exists
    '''

    msg, _ = conversation.messages.get_or_create(writer=self.writer, message=self.message)

    return msg

    # Check there is not already the same message
    if conversation.messages.filter(writer=self.writer, message=self.message).count() > 0:
      return False

    # Copy the message
    data = {
      'writer' : self.writer,
      'message' : self.message,
    }
    conversation.messages.create(**data)
