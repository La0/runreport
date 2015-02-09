# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0008_auto_20150131_2015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sportsession',
            name='plan_session',
        ),
    ]
