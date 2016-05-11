# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0019_auto_20151026_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentsubscription',
            name='status',
            field=models.CharField(default=b'created', max_length=20, choices=[(b'free', 'Free'), (b'active', 'Active'), (b'paid', 'Paid'), (b'expired', 'Expired'), (b'error', 'Error')]),
        ),
    ]
