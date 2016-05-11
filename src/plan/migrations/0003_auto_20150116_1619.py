# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0007_auto_20150116_1619'),
        ('plan', '0002_auto_20140930_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='planusage',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='planusage',
            name='user',
        ),
        migrations.DeleteModel(
            name='PlanUsage',
        ),
        migrations.AlterUniqueTogether(
            name='planweek',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='planweek',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='plan',
            name='task',
        ),
        migrations.RemoveField(
            model_name='plansession',
            name='distance',
        ),
        migrations.RemoveField(
            model_name='plansession',
            name='time',
        ),
        migrations.AddField(
            model_name='plansession',
            name='plan',
            field=models.ForeignKey(related_name=b'sessions', default=None, to='plan.Plan'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='plansession',
            name='week',
            field=models.IntegerField(),
        ),
        migrations.DeleteModel(
            name='PlanWeek',
        ),
        migrations.AlterUniqueTogether(
            name='plan',
            unique_together=None,
        ),
        migrations.AlterUniqueTogether(
            name='plansession',
            unique_together=None,
        ),
    ]
