# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gear', '0005_remove_gearitem_sessions'),
        ('sport', '0016_auto_20150722_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportsession',
            name='gear',
            field=models.ManyToManyField(related_name='sessions', to='gear.GearItem'),
        ),
    ]
