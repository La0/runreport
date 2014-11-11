# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0005_sport_strava_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='garminactivity',
            name='session',
        ),
        migrations.RemoveField(
            model_name='garminactivity',
            name='sport',
        ),
        migrations.RemoveField(
            model_name='garminactivity',
            name='user',
        ),
        migrations.DeleteModel(
            name='GarminActivity',
        ),
    ]
