# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0009_auto_20141023_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracksplit',
            name='distance',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='distance_total',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='elevation_gain',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='elevation_loss',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='elevation_max',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='elevation_min',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='energy',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='speed',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='speed_max',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='time',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tracksplit',
            name='time_total',
            field=models.FloatField(default=0),
        ),
    ]
