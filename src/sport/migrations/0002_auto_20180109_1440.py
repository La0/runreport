# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-09 13:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sport', '0001_initial'),
        ('gear', '0003_auto_20180109_1440'),
        ('messages', '0002_auto_20180109_1440'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='sportweek',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sportweek', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sportsession',
            name='comments_private',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_private', to='messages.Conversation'),
        ),
        migrations.AddField(
            model_name='sportsession',
            name='comments_public',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_public', to='messages.Conversation'),
        ),
        migrations.AddField(
            model_name='sportsession',
            name='day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='sport.SportDay'),
        ),
        migrations.AddField(
            model_name='sportsession',
            name='gear',
            field=models.ManyToManyField(related_name='sessions', to='gear.GearItem'),
        ),
        migrations.AddField(
            model_name='sportsession',
            name='race_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sport.RaceCategory', verbose_name='Race category'),
        ),
        migrations.AddField(
            model_name='sportsession',
            name='sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sport.Sport'),
        ),
        migrations.AddField(
            model_name='sportday',
            name='sports',
            field=models.ManyToManyField(through='sport.SportSession', to='sport.Sport'),
        ),
        migrations.AddField(
            model_name='sportday',
            name='week',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='sport.SportWeek'),
        ),
        migrations.AddField(
            model_name='sport',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sport.Sport'),
        ),
        migrations.AlterUniqueTogether(
            name='sportweek',
            unique_together=set([('user', 'year', 'week')]),
        ),
        migrations.AlterUniqueTogether(
            name='sportday',
            unique_together=set([('week', 'date')]),
        ),
    ]
