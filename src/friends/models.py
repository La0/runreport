from django.db import models
from users.notification import UserNotifications
from friends.tasks import notify_friend_request


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        'users.Athlete',
        on_delete=models.CASCADE,
        related_name='requests_sent'
    )
    recipient = models.ForeignKey(
        'users.Athlete',
        on_delete=models.CASCADE,
        related_name='requests_received')

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('sender', 'recipient'), )

    def __str__(self):
        return '%s > %s' % (self.sender, self.recipient)

    def accept(self):
        # Add friend to symmetric relation
        self.sender.friends.add(self.recipient)

        # Notify sender
        un = UserNotifications(self.sender)
        un.add_friend_request(self, accepted=True)

        # Send email
        notify_friend_request(self.sender, self.recipient, accepted=True)

        # Delete
        self.delete()

    def notify(self):

        # Notify recipient
        un = UserNotifications(self.recipient)
        un.add_friend_request(self)

        # Send email
        notify_friend_request(self.sender, self.recipient)
