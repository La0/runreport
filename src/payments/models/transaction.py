from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
import json

TRANSACTION_STATUS = (
    ('CREATED', _('Created')),
    ('FAILED', _('Failed')),
    ('SUCCEEDED', _('Succeeded')),
)


class PaymentTransaction(models.Model):
    '''
    Every payment made for a club
    '''
    club = models.ForeignKey('club.Club', related_name='transactions')
    period = models.ForeignKey(
        'payments.PaymentPeriod',
        related_name='transactions',
        null=True,
        blank=True)
    status = models.CharField(
        choices=TRANSACTION_STATUS,
        max_length=20,
        default='CREATED')
    mangopay_id = models.CharField(unique=True, max_length=50)

    response = models.TextField()  # raw response

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @cached_property
    def data(self):
        # Helper to access the response content
        if not self.response:
            return None
        return json.loads(self.response)

    @cached_property
    def amount(self):
        if not self.data:
            return None

        funds = self.data.get('DebitedFunds')
        if not funds:
            return None

        return funds['Amount'] / 100.0  # in euros, not cents
