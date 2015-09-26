# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gear', '0003_auto_20150925_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gearitem',
            name='sessions',
            field=models.ManyToManyField(related_name='items', to='sport.SportSession', blank=True),
        ),
    ]
