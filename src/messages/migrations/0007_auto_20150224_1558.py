# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messages', '0006_conversation_session_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='type',
            field=models.CharField(max_length=50, choices=[(b'mail', b'Mail'), (b'comments_public', b'Public comments'), (b'comments_private', b'Private comments'), (b'plan_session', b'Plan session')]),
        ),
    ]
