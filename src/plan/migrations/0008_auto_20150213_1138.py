# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0007_auto_20150209_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='plansession',
            name='distance',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='plansession',
            name='time',
            field=models.DurationField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
