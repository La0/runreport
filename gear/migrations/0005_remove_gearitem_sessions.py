# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gear', '0004_auto_20150926_1047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gearitem',
            name='sessions',
        ),
    ]
