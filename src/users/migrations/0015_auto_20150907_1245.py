# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20150722_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 7, 10, 45, 54, 520988, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_avatar',
            field=models.CharField(default=b'public', max_length=50, verbose_name='avatar visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
    ]
