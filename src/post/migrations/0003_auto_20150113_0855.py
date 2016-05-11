# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_auto_20150112_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmedia',
            name='name',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postmedia',
            name='type',
            field=models.CharField(max_length=25, choices=[(b'image source', 'Source Image'), (b'image thumb', 'Thumbnail Image'), (b'image crop', 'Cropped Image')]),
        ),
    ]
