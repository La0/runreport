# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0002_track_simple'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='provider',
            field=models.CharField(default=b'manual', max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='track',
            name='provider_id',
            field=models.CharField(max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
