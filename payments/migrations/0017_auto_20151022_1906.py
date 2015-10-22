# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0016_auto_20151022_1806'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymenttransaction',
            name='amount',
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='status',
            field=models.CharField(default=b'CREATED', max_length=20, choices=[(b'CREATED', 'Created'), (b'FAILED', 'Failed'), (b'SUCEEDED', 'Succeeded')]),
        ),
    ]
