# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_athlete_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='language',
            field=models.CharField(default=b'fr', max_length=2, choices=[(b'fr', 'French'), (b'en', 'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='athlete',
            name='auto_send',
            field=models.BooleanField(default=False, verbose_name='automatically send reports to your trainers at the end of weeks'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='avatar',
            field=models.ImageField(upload_to=users.models.build_avatar_path, verbose_name='profile picture'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='birthday',
            field=models.DateField(null=True, verbose_name='birthday', blank=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='category',
            field=models.ForeignKey(verbose_name='category', blank=True, to='users.UserCategory', null=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='comment',
            field=models.TextField(null=True, verbose_name='comment', blank=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='default_sport',
            field=models.ForeignKey(default=3, verbose_name='default sport', to='sport.Sport'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='demo',
            field=models.BooleanField(default=False, verbose_name='demo user'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='frequency',
            field=models.IntegerField(blank=True, null=True, verbose_name='cardiac frequency', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='frequency_rest',
            field=models.IntegerField(blank=True, null=True, verbose_name='cardiac frequency at rest', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='garmin_login',
            field=models.CharField(max_length=255, null=True, verbose_name='garmin login', blank=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='garmin_password',
            field=models.TextField(null=True, verbose_name='garmin password', blank=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='height',
            field=models.IntegerField(blank=True, help_text='Unit: cm', null=True, verbose_name='height', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='license',
            field=models.CharField(max_length=12, null=True, verbose_name='license', blank=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='nb_sessions',
            field=models.IntegerField(blank=True, null=True, verbose_name='number of sessions per week', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_avatar',
            field=models.CharField(default=b'club', max_length=50, verbose_name='profile picture visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_calendar',
            field=models.CharField(default=b'private', max_length=50, verbose_name='calendar visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_comments',
            field=models.CharField(default=b'club', max_length=50, verbose_name='comments visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_profile',
            field=models.CharField(default=b'club', help_text='Indicates if your public profile is visible, and by who.', max_length=50, verbose_name='profile visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_races',
            field=models.CharField(default=b'club', max_length=50, verbose_name='races visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_records',
            field=models.CharField(default=b'club', max_length=50, verbose_name='records visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_stats',
            field=models.CharField(default=b'club', max_length=50, verbose_name='stats visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='privacy_tracks',
            field=models.CharField(default=b'club', max_length=50, verbose_name='tracks visibility', choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='vma',
            field=models.FloatField(blank=True, help_text='Ex: 12.5 km/h', null=True, verbose_name='vma', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='weight',
            field=models.IntegerField(blank=True, help_text='Unit: kg', null=True, verbose_name='weight', validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
