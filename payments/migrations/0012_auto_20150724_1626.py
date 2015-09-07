# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0011_auto_20150722_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentoffer',
            name='target',
            field=models.CharField(default=b'athlete', max_length=10, choices=[(b'club', 'Club'), (b'athlete', 'Athlete')]),
        ),
        migrations.AlterField(
            model_name='paymentsubscription',
            name='paymill_id',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paymentsubscription',
            name='end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paymentsubscription',
            name='start',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 26, 10, 52, 28, 289805, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
