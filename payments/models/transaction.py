from django.db import models
from django.utils.translation import ugettext_lazy as _

TRANSACTION_STATUS = (
  ('CREATED', _('Created')),
  ('FAILED', _('Failed')),
  ('SUCEEDED', _('Succeeded')),
)


class PaymentTransaction(models.Model):
  '''
  Every payment made for a club
  '''
  club = models.ForeignKey('club.Club', related_name='transactions')
  status = models.CharField(choices=TRANSACTION_STATUS, max_length=20, default='CREATED')
  mangopay_id = models.CharField(unique=True, max_length=50)

  response = models.TextField() # raw response

  # Dates
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

