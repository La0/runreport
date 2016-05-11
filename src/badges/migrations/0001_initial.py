# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
                ('value', models.CharField(max_length=250, null=True, blank=True)),
                ('position', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='BadgeCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='BadgeUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(to='badges.Badge')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='badge',
            name='category',
            field=models.ForeignKey(to='badges.BadgeCategory'),
        ),
        migrations.AddField(
            model_name='badge',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='badges.BadgeUser'),
        ),
        migrations.AlterUniqueTogether(
            name='badgeuser',
            unique_together=set([('badge', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='badge',
            unique_together=set([('category', 'position')]),
        ),
        migrations.AlterModelOptions(
            name='badge',
            options={'ordering': ('position',)},
        ),
    ]
