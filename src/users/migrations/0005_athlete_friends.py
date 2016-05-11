# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_athlete_privacy_tracks'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='friends',
            field=models.ManyToManyField(related_name='friends_rel_+', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
