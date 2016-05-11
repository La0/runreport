# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0006_auto_20141111_1635'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sportweek',
            name='plan_week',
        ),
        migrations.AlterField(
            model_name='sportsession',
            name='comment',
            field=models.TextField(null=True, verbose_name='session comment', blank=True),
        ),
        migrations.AlterField(
            model_name='sportsession',
            name='race_category',
            field=models.ForeignKey(verbose_name='Race category', blank=True, to='sport.RaceCategory', null=True),
        ),
        migrations.AlterField(
            model_name='sportsession',
            name='type',
            field=models.CharField(default=b'training', max_length=12, choices=[(b'training', 'training'), (b'race', 'race'), (b'rest', 'rest')]),
        ),
    ]
