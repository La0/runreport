from django.db import models

class FriendRequest(models.Model):
  sender = models.ForeignKey('users.Athlete', related_name='requests_sent')
  recipient = models.ForeignKey('users.Athlete', related_name='requests_received')

  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = (('sender', 'recipient'), )

  def __unicode__(self):
    return '%s > %s' % (self.sender, self.recipient)

  def notify(self):
    print 'Notify !'
