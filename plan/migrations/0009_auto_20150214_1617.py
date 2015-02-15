# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20150214_1617'),
        ('plan', '0008_auto_20150213_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='plansession',
            name='hour',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='plansession',
            name='place',
            field=models.ForeignKey(related_name=b'plan_sessions', blank=True, to='events.Place', null=True),
            preserve_default=True,
        ),
    ]
