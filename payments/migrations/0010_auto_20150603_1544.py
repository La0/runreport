# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_auto_20150603_1512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentsubscription',
            name='active',
        ),
        migrations.AddField(
            model_name='paymentsubscription',
            name='status',
            field=models.CharField(default=b'inactive', max_length=20, choices=[(b'active', 'Active'), (b'inactive', 'Inactive'), (b'expired', 'Expired'), (b'failed', 'Failed')]),
        ),
    ]
