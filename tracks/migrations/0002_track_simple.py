# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='simple',
            field=django.contrib.gis.db.models.fields.LineStringField(srid=4326, null=True, blank=True),
            preserve_default=True,
        ),
    ]
