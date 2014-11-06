# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0008_auto_20141023_1728'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='trackstat',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='trackstat',
            name='track',
        ),
        migrations.DeleteModel(
            name='TrackStat',
        ),
        migrations.AddField(
            model_name='track',
            name='split_total',
            field=models.OneToOneField(related_name=b'direct_track', null=True, blank=True, to='tracks.TrackSplit'),
            preserve_default=True,
        ),
    ]
