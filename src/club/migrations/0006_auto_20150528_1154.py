# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


def clubs_creation_date(apps, schema_editor):
    '''
    Use manager membership date as club creation date
    '''
    Club = apps.get_model('club.Club')
    for club in Club.objects.all():
        m = club.clubmembership_set.get(user_id=club.manager_id)
        club.created = m.created
        club.save()

class Migration(migrations.Migration):

    dependencies = [
        ('club', '0005_auto_20150312_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 28, 11, 54, 51, 959146), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='club',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 28, 11, 54, 58, 685163), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clubinvite',
            name='recipient',
            field=models.EmailField(max_length=254),
        ),
        migrations.RunPython(clubs_creation_date),
    ]
