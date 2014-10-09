from django.db import models
from users.models import Athlete
from sport.models import SportSession
from users.notification import UserNotifications

class Message(models.Model):
  sender = models.ForeignKey(Athlete, related_name='messages_sent')
  recipient = models.ForeignKey(Athlete, related_name='messages_received')
  message = models.TextField()

  # Only recipient can see ?
  private = models.BooleanField(default=False)

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  # Simple incremental revision on edits
  revision = models.IntegerField(default=1)

  # Optional links to objects
  session = models.ForeignKey(SportSession, null=True, blank=True, related_name='comments')

  def notify(self):
    # Always send to recipient
    un = UserNotifications(self.recipient)
    un.add_message(self)

    if self.session:
      # All members of discussion on session
      for c in self.session.comments.exclude(sender=self.recipient).distinct('sender'):
        un = UserNotifications(c.sender)
        un.add_message(self)
