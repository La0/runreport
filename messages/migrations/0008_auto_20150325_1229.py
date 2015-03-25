# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messages', '0007_auto_20150224_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='type',
            field=models.CharField(max_length=50, choices=[(b'mail', b'Mail'), (b'comments_public', b'Public comments'), (b'comments_private', b'Private comments'), (b'comments_week', b'Week comments'), (b'plan_session', b'Plan session'), (b'post', b'Post')]),
        ),
    ]
