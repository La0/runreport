# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0013_sportsession_gcal_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportsession',
            name='note',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sportsession',
            name='type',
            field=models.CharField(default=b'training', max_length=12, choices=[(b'training', 'Training'), (b'race', 'Race'), (b'rest', 'Rest')]),
        ),
    ]
