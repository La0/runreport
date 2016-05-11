# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentOffer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paymill_id', models.CharField(max_length=50, null=True, blank=True)),
                ('slug', models.SlugField(max_length=20)),
                ('name', models.CharField(max_length=250)),
                ('amount', models.FloatField()),
                ('currency', models.CharField(max_length=10)),
                ('interval', models.CharField(max_length=20)),
            ],
        ),
    ]
