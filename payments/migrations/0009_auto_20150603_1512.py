# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0008_auto_20150603_1220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymenttransaction',
            name='subscription',
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='status',
            field=models.CharField(default=b'open', max_length=20, choices=[(b'open', 'Open'), (b'pending', 'Pending'), (b'closed', 'Closed'), (b'failed', 'Failed'), (b'partial_refunded', 'Partial Refund'), (b'refunded', 'Refunded'), (b'preauthorize', 'Pre-Authorize'), (b'chargeback', 'Chargeback')]),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='user',
            field=models.ForeignKey(related_name='payment_transactions', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
