# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField(unique=True, max_length=20)),
                ('max_staff', models.IntegerField(default=1)),
                ('max_trainer', models.IntegerField(default=2)),
                ('max_athlete', models.IntegerField(default=20)),
                ('address', models.CharField(max_length=250)),
                ('zipcode', models.CharField(max_length=10)),
                ('city', models.CharField(max_length=250)),
                ('demo', models.BooleanField(default=False)),
                ('private', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClubInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recipient', models.EmailField(max_length=75)),
                ('name', models.CharField(max_length=250, null=True, blank=True)),
                ('type', models.CharField(max_length=15, choices=[(b'create', b'Create a club (Beta)')])),
                ('slug', models.CharField(unique=True, max_length=30, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('sent', models.DateTimeField(null=True, blank=True)),
                ('used', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClubLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('url', models.URLField(max_length=250)),
                ('position', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClubMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=10, choices=[(b'athlete', 'Athl\xe8te'), (b'trainer', 'Entra\xeeneur'), (b'staff', 'Staff'), (b'archive', 'Archive'), (b'prospect', 'Nouveau')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('club', models.ForeignKey(to='club.Club')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
