# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messages', '0003_auto_20141015_1014'),
        ('sport', '0002_auto_20140930_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportsession',
            name='comments_private',
            field=models.ForeignKey(related_name=b'session_private', blank=True, to='messages.Conversation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sportsession',
            name='comments_public',
            field=models.ForeignKey(related_name=b'session_public', blank=True, to='messages.Conversation', null=True),
            preserve_default=True,
        ),
    ]
