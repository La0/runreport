# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0006_auto_20141022_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackSplit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('distance', models.FloatField()),
                ('distance_total', models.FloatField()),
                ('time', models.FloatField()),
                ('time_total', models.FloatField()),
                ('speed', models.FloatField()),
                ('speed_max', models.FloatField()),
                ('elevation_gain', models.FloatField()),
                ('elevation_loss', models.FloatField()),
                ('energy', models.FloatField()),
                ('track', models.ForeignKey(to='tracks.Track')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tracksplit',
            unique_together=set([('track', 'position')]),
        ),
    ]
