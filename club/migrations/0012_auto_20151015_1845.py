# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0011_auto_20151014_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='card_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='clubmembership',
            name='role',
            field=models.CharField(max_length=10, choices=[(b'athlete', 'Athlete'), (b'trainer', 'Trainer'), (b'staff', 'Staff'), (b'archive', 'Archive'), (b'prospect', 'Prospect')]),
        ),
    ]
