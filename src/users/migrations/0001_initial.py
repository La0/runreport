# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Athlete',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid username.', b'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(unique=True, max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('birthday', models.DateField(null=True, blank=True)),
                ('vma', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('frequency', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('frequency_rest', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('height', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('weight', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('comment', models.TextField(null=True, blank=True)),
                ('nb_sessions', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('license', models.CharField(max_length=12, null=True, blank=True)),
                ('auto_send', models.BooleanField(default=False)),
                ('garmin_login', models.CharField(max_length=255, null=True, blank=True)),
                ('garmin_password', models.TextField(null=True, blank=True)),
                ('demo', models.BooleanField(default=False)),
                ('avatar', models.ImageField(upload_to=users.models.build_avatar_path)),
                ('privacy_profile', models.CharField(default=b'club', max_length=50, choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Priv\xe9')])),
                ('privacy_avatar', models.CharField(default=b'club', max_length=50, choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Priv\xe9')])),
                ('privacy_races', models.CharField(default=b'club', max_length=50, choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Priv\xe9')])),
                ('privacy_records', models.CharField(default=b'club', max_length=50, choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Priv\xe9')])),
                ('privacy_stats', models.CharField(default=b'club', max_length=50, choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Priv\xe9')])),
                ('privacy_calendar', models.CharField(default=b'private', max_length=50, choices=[(b'public', 'Public'), (b'club', 'Club'), (b'private', 'Priv\xe9')])),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=120)),
                ('min_year', models.IntegerField()),
                ('max_year', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='athlete',
            name='category',
            field=models.ForeignKey(blank=True, to='users.UserCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='athlete',
            name='default_sport',
            field=models.ForeignKey(default=3, to='sport.Sport'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='athlete',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='athlete',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
