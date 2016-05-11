# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='planusage',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='plansession',
            name='week',
            field=models.ForeignKey(related_name=b'sessions', to='plan.PlanWeek'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='plansession',
            unique_together=set([('week', 'day')]),
        ),
        migrations.AddField(
            model_name='plan',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='plan',
            unique_together=set([('creator', 'slug')]),
        ),
    ]
