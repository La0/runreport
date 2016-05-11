# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0005_auto_20141017_1837'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('value', models.FloatField()),
                ('unit', models.CharField(max_length=50)),
                ('track', models.ForeignKey(related_name=b'stats', to='tracks.Track')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='trackstat',
            unique_together=set([('track', 'name')]),
        ),
    ]
