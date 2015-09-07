# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0010_auto_20150603_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentsubscription',
            name='status',
            field=models.CharField(default=b'created', max_length=20, choices=[(b'created', 'Created'), (b'active', 'Active'), (b'inactive', 'Inactive'), (b'expired', 'Expired'), (b'failed', 'Failed')]),
        ),
    ]
