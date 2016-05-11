# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0008_auto_20150726_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='mangopay_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='club',
            name='wallet_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
