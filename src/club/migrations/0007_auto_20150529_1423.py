# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0006_auto_20150528_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='mailing_list',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='clubgroup',
            name='mailing_list',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
