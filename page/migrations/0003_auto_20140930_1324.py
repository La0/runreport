# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0002_auto_20140930_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]
