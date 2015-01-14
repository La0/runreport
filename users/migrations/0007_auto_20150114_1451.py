# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20141211_1728'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='athlete',
            name='privacy_profile',
        ),
        migrations.AlterField(
            model_name='athlete',
            name='language',
            field=models.CharField(default=b'fr', max_length=2, verbose_name='language used', choices=[(b'fr', 'French'), (b'en', 'English')]),
        ),
    ]
