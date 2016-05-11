# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0018_paymenttransaction_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentsubscription',
            name='nb_staff',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='paymentsubscription',
            name='nb_trainers',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='status',
            field=models.CharField(default=b'CREATED', max_length=20, choices=[(b'CREATED', 'Created'), (b'FAILED', 'Failed'), (b'SUCCEEDED', 'Succeeded')]),
        ),
    ]
