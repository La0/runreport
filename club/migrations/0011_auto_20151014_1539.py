# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields

class Migration(migrations.Migration):

    dependencies = [
        ('club', '0010_club_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='club',
            name='max_athlete',
        ),
        migrations.RemoveField(
            model_name='club',
            name='max_staff',
        ),
        migrations.RemoveField(
            model_name='club',
            name='max_trainer',
        ),
        migrations.AlterField(
            model_name='club',
            name='country',
            field=django_countries.fields.CountryField(default=b'FR', max_length=2, verbose_name='Country'),
        ),
    ]
