# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0004_auto_20141017_1807'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='trackfile',
            unique_together=set([('track', 'name')]),
        ),
    ]
