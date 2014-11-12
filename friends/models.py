from django.db import models
from users.notification import UserNotifications

class FriendRequest(models.Model):
  sender = models.ForeignKey('users.Athlete', related_name='requests_sent')
  recipient = models.ForeignKey('users.Athlete', related_name='requests_received')

  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = (('sender', 'recipient'), )

  def __unicode__(self):
    return '%s > %s' % (self.sender, self.recipient)

  def accept(self):
    # Add friend to symmetric relation
    self.sender.friends.add(self.recipient)

    # Notify sender
    un = UserNotifications(self.sender)
    un.add_friend_request(self, accepted=True)

    # Send email
    # TODO

    # Delete
    self.delete()

  def notify(self):

    # Notify recipient
    un = UserNotifications(self.recipient)
    un.add_friend_request(self)

    # Send email
    # TODO
