# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('club', '0002_auto_20140930_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('club', models.ForeignKey(related_name=b'groups', to='club.Club')),
                ('creator', models.ForeignKey(related_name=b'groups_owned', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name=b'club_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='clubgroup',
            unique_together=set([('club', 'slug')]),
        ),
        migrations.AlterField(
            model_name='clublink',
            name='name',
            field=models.CharField(max_length=250, verbose_name='Link name'),
        ),
        migrations.AlterField(
            model_name='clublink',
            name='url',
            field=models.URLField(max_length=250, verbose_name='Link address'),
        ),
    ]
