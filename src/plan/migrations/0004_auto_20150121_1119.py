# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0007_auto_20150116_1619'),
        ('plan', '0003_auto_20150116_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='plansession',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 21, 11, 19, 9, 500880), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plansession',
            name='sport',
            field=models.ForeignKey(default=3, to='sport.Sport'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plansession',
            name='type',
            field=models.CharField(default=b'training', max_length=12, choices=[(b'training', 'training'), (b'race', 'race'), (b'rest', 'rest')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='plansession',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 21, 11, 19, 49, 354665), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='plan',
            name='creator',
            field=models.ForeignKey(related_name=b'plans', to=settings.AUTH_USER_MODEL),
        ),
    ]
