# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0005_plan_start'),
        ('sport', '0007_auto_20150116_1619'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sportday',
            name='plan_session',
        ),
        migrations.AddField(
            model_name='sportsession',
            name='plan_session',
            field=models.ForeignKey(blank=True, to='plan.PlanSession', null=True),
            preserve_default=True,
        ),
    ]
