# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20150907_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='athlete',
            name='paymill_id',
        ),
        migrations.AddField(
            model_name='athlete',
            name='country',
            field=django_countries.fields.CountryField(default=b'FR', max_length=2),
        ),
        migrations.AddField(
            model_name='athlete',
            name='nationality',
            field=django_countries.fields.CountryField(default=b'FR', max_length=2),
        ),
    ]
