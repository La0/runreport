# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_athlete_daily_trainer_mail'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='athlete',
            managers=[
                (b'objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='athlete',
            name='gcal_token',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='auto_send',
            field=models.BooleanField(default=False, verbose_name='auto send emails'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='email address', blank=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
    ]
