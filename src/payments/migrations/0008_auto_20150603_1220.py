# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_auto_20150603_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentevent',
            name='applied',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paymentsubscription',
            name='paymill_id',
            field=models.CharField(unique=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='paymill_id',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
    ]
