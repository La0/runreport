# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0009_auto_20151011_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='country',
            field=django_countries.fields.CountryField(default=b'FR', max_length=2),
        ),
    ]
