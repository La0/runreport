# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0011_auto_20150325_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sportweek',
            name='conversation',
            field=models.OneToOneField(related_name=b'week', null=True, blank=True, to='messages.Conversation'),
        ),
    ]
