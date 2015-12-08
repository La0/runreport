# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0017_sportsession_gear'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportsession',
            name='comment_html',
            field=models.TextField(null=True, blank=True),
        ),
    ]
