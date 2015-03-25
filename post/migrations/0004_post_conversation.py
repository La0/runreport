# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messages', '0008_auto_20150325_1229'),
        ('post', '0003_auto_20150113_0855'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='conversation',
            field=models.OneToOneField(related_name=b'post', null=True, blank=True, to='messages.Conversation'),
            preserve_default=True,
        ),
    ]
