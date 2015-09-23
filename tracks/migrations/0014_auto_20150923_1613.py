# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0013_track_thumb'),
    ]

    operations = [
        # Force unique on 1-1 relation between
        # Track & SportSession
        # Django seems to mess this up :(
        migrations.RunSQL('alter table tracks_track add constraint track_session_unique unique (session_id);'),
    ]
