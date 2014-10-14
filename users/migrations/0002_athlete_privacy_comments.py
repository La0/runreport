# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='privacy_comments',
            field=models.CharField(default=b'club', max_length=50, choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Priv\xe9')]),
            preserve_default=True,
        ),
    ]
