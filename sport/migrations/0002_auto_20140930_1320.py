# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0001_initial'),
        ('plan', '0002_auto_20140930_1320'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='sportweek',
            name='user',
            field=models.ForeignKey(related_name=b'sportweek', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sportweek',
            unique_together=set([('user', 'year', 'week')]),
        ),
        migrations.AddField(
            model_name='sportsession',
            name='day',
            field=models.ForeignKey(related_name=b'sessions', to='sport.SportDay'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sportsession',
            name='race_category',
            field=models.ForeignKey(blank=True, to='sport.RaceCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sportsession',
            name='sport',
            field=models.ForeignKey(to='sport.Sport'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sportday',
            name='plan_session',
            field=models.ForeignKey(blank=True, to='plan.PlanSession', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sportday',
            name='sports',
            field=models.ManyToManyField(to='sport.Sport', through='sport.SportSession'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sportday',
            name='week',
            field=models.ForeignKey(related_name=b'days', to='sport.SportWeek'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sportday',
            unique_together=set([('week', 'date')]),
        ),
        migrations.AddField(
            model_name='sport',
            name='parent',
            field=models.ForeignKey(to='sport.Sport', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='garminactivity',
            name='session',
            field=models.OneToOneField(related_name=b'garmin_activity', to='sport.SportSession'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='garminactivity',
            name='sport',
            field=models.ForeignKey(to='sport.Sport'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='garminactivity',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
