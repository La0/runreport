# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0012_auto_20150325_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportsession',
            name='gcal_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
