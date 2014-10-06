# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import interval.fields


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GarminActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('garmin_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=255)),
                ('time', interval.fields.IntervalField()),
                ('distance', models.FloatField()),
                ('speed', models.TimeField()),
                ('md5_raw', models.CharField(max_length=32)),
                ('md5_laps', models.CharField(max_length=32, null=True)),
                ('md5_details', models.CharField(max_length=32, null=True)),
                ('date', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'garmin_activity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RaceCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('distance', models.FloatField(null=True, blank=True)),
            ],
            options={
                'db_table': 'sport_race_category',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField(unique=True)),
                ('depth', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'sport_list',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SportDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
            ],
            options={
                'db_table': 'sport_day',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SportSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', interval.fields.IntervalField(null=True, blank=True)),
                ('distance', models.FloatField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('type', models.CharField(default=b'training', max_length=12, choices=[(b'training', b'Entrainement'), (b'race', b'Course'), (b'rest', b'Repos')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'sport_session',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SportWeek',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(default=2013)),
                ('week', models.IntegerField(default=0)),
                ('published', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('task', models.CharField(max_length=36, null=True, blank=True)),
                ('plan_week', models.ForeignKey(blank=True, to='plan.PlanWeek', null=True)),
            ],
            options={
                'db_table': 'sport_week',
            },
            bases=(models.Model,),
        ),
    ]
