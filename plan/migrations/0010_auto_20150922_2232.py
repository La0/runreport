# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0009_auto_20150214_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='plansession',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='plansession',
            name='type',
            field=models.CharField(default=b'training', max_length=12, choices=[(b'training', 'Training'), (b'race', 'Race'), (b'rest', 'Rest')]),
        ),
        migrations.AlterField(
            model_name='plansessionapplied',
            name='status',
            field=models.CharField(default=b'applied', max_length=20, choices=[(b'applied', 'Applied'), (b'done', 'Done'), (b'failed', 'Failed')]),
        ),
    ]
