# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0004_auto_20150121_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='start',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
