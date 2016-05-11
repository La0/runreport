# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0007_auto_20150529_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='address',
            field=models.CharField(max_length=250, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='club',
            name='city',
            field=models.CharField(max_length=250, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='club',
            name='max_athlete',
            field=models.IntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='club',
            name='max_trainer',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='club',
            name='name',
            field=models.CharField(max_length=250, verbose_name='Club name'),
        ),
        migrations.AlterField(
            model_name='club',
            name='private',
            field=models.BooleanField(default=False, help_text='When private, a club is only accessible y its members', verbose_name='Private club'),
        ),
        migrations.AlterField(
            model_name='club',
            name='slug',
            field=models.SlugField(help_text=b"Represents the club's name in urls", unique=True, max_length=20, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='club',
            name='zipcode',
            field=models.CharField(max_length=10, verbose_name='Zip code'),
        ),
    ]
