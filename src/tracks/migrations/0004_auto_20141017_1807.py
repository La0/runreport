# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0003_auto_20141017_1755'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'details', max_length=50, db_index=True)),
                ('md5', models.CharField(max_length=32)),
                ('track', models.ForeignKey(related_name=b'files', to='tracks.Track')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='track',
            unique_together=set([('provider', 'provider_id')]),
        ),
    ]
