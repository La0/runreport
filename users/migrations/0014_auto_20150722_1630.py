# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athlete',
            name='privacy_avatar',
            field=models.CharField(default=b'public', max_length=50, verbose_name='profile picture visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_comments',
            field=models.CharField(default=b'public', max_length=50, verbose_name='comments visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_races',
            field=models.CharField(default=b'public', max_length=50, verbose_name='races visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_records',
            field=models.CharField(default=b'public', max_length=50, verbose_name='records visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_stats',
            field=models.CharField(default=b'public', max_length=50, verbose_name='stats visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
    ]
