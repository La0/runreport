# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0004_auto_20141017_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='sport',
            name='strava_name',
            field=models.CharField(max_length=250, null=True, blank=True),
            preserve_default=True,
        ),
    ]
