# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import badges.models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='image',
            field=models.ImageField(default=b'badges/default.png', upload_to=badges.models.badge_image_path),
        ),
        migrations.AlterField(
            model_name='badge',
            name='category',
            field=models.ForeignKey(related_name='badges', to='badges.BadgeCategory'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='users',
            field=models.ManyToManyField(related_name='badges', through='badges.BadgeUser', to=settings.AUTH_USER_MODEL),
        ),
    ]
