# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0003_auto_20141015_1017'),
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('session', models.OneToOneField(related_name=b'track', to='sport.SportSession')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
