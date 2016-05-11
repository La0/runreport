# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('club', '0004_auto_20150115_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='clubinvite',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='clubinvite',
            name='type',
            field=models.CharField(max_length=15, choices=[(b'create', b'Create a club (Beta)'), (b'join', b'Join a club')]),
        ),
    ]
