# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0003_auto_20141015_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sportsession',
            name='comments_private',
            field=models.OneToOneField(related_name=b'session_private', null=True, blank=True, to='messages.Conversation'),
        ),
        migrations.AlterField(
            model_name='sportsession',
            name='comments_public',
            field=models.OneToOneField(related_name=b'session_public', null=True, blank=True, to='messages.Conversation'),
        ),
    ]
