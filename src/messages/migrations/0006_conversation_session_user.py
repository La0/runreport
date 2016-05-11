# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('messages', '0005_conversation_mail_recipient'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='session_user',
            field=models.ForeignKey(related_name=b'session_conversations', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
