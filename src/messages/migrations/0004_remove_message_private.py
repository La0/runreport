# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messages', '0003_auto_20141015_1014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='private',
        ),
    ]
