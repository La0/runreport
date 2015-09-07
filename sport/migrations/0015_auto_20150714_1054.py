# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def use_tracks_evelation(apps, schema_editor):
  '''
  Use elevation data from tracks total splits
  to init new fields
  '''
  TrackSplit = apps.get_model('tracks', 'TrackSplit')
  splits = TrackSplit.objects.filter(position=0)
  for split in splits:
    session = split.track.session
    session.elevation_gain = split.elevation_gain
    session.elevation_loss = split.elevation_loss
    session.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0014_auto_20150709_2204'),
        ('tracks', '0013_track_thumb'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportsession',
            name='elevation_gain',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sportsession',
            name='elevation_loss',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.RunPython(use_tracks_evelation),
    ]
