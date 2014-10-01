from django.db import models
from users.models import Athlete
from sport.models import SportSession

class Message(models.Model):
  sender = models.ForeignKey(Athlete, related_name='messages_sent')
  recipient = models.ForeignKey(Athlete, related_name='messages_received')
  message = models.TextField()

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  # Simple incremental revision on edits
  revision = models.IntegerField(default=1)

  # Optional links to objects
  session = models.ForeignKey(SportSession, null=True, blank=True, related_name='comments')
