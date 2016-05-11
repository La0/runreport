# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tracks.models.base


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0012_track_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='thumb',
            field=models.ImageField(null=True, upload_to=tracks.models.base.build_thumb_path, blank=True),
        ),
    ]
