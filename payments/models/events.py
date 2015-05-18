from django.db import models

class PaymentEvent(models.Model):
  '''
  Represents an event sent from Paymill hooks
  '''
  event_id = models.CharField(max_length=32, unique=True)
  type = models.CharField(max_length=50)

  # Links
  user = models.ForeignKey('users.Athlete', null=True, blank=True, related_name='payment_events')
  subscription = models.ForeignKey('payments.PaymentSubscription', null=True, blank=True, related_name='events')

  # Raw event resource
  raw_data = models.TextField()

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
