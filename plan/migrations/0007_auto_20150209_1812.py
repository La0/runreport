# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0006_plansessionapplied'),
    ]

    operations = [
        migrations.AddField(
            model_name='plansessionapplied',
            name='trainer_notified',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='plansessionapplied',
            name='status',
            field=models.CharField(default=b'applied', max_length=20, choices=[(b'applied', 'To Do'), (b'done', 'Done'), (b'failed', 'Missed')]),
        ),
    ]
