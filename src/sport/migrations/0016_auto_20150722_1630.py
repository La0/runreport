# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0015_auto_20150714_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sportsession',
            name='distance',
            field=models.FloatField(null=True, verbose_name='Distance', blank=True),
        ),
        migrations.AlterField(
            model_name='sportsession',
            name='elevation_gain',
            field=models.FloatField(null=True, verbose_name='Elevation gain', blank=True),
        ),
        migrations.AlterField(
            model_name='sportsession',
            name='elevation_loss',
            field=models.FloatField(null=True, verbose_name='Elevation loss', blank=True),
        ),
        migrations.AlterField(
            model_name='sportsession',
            name='time',
            field=models.DurationField(null=True, verbose_name='Time', blank=True),
        ),
    ]
