# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('messages', '0004_remove_message_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='mail_recipient',
            field=models.ForeignKey(related_name=b'mail_conversations', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
