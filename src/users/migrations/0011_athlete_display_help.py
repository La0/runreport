# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_athlete_gcal_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='display_help',
            field=models.BooleanField(default=True, verbose_name='Display contextual help'),
        ),
    ]
