# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='address',
            field=models.CharField(max_length=255, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='place',
            name='city',
            field=models.CharField(max_length=255, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='place',
            name='zipcode',
            field=models.CharField(max_length=10, verbose_name='Zip Code'),
        ),
    ]
