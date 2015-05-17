# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tracks.models.base


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0011_remove_track_raw'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='image',
            field=models.ImageField(null=True, upload_to=tracks.models.base.build_image_path, blank=True),
        ),
    ]
