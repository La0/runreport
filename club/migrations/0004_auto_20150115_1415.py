# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0003_auto_20150114_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clubgroup',
            name='description',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='clubgroup',
            name='members',
            field=models.ManyToManyField(related_name=b'groups', to=b'club.ClubMembership'),
        ),
        migrations.AlterField(
            model_name='clubgroup',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Group name'),
        ),
        migrations.AlterField(
            model_name='clubgroup',
            name='slug',
            field=models.SlugField(verbose_name='Name in the url'),
        ),
    ]
