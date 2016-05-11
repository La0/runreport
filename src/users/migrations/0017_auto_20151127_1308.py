# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_demo_states(apps, schema_editor):
  '''
  Update current demo states on users
  '''
  from users.models import Athlete # need logic here
  for a in Athlete.objects.all():
    a.check_demo_steps('athlete', notify=False)
    if a.is_trainer:
      a.check_demo_steps('trainer', notify=False)

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20151012_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='demo_athlete_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='athlete',
            name='demo_trainer_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='athlete',
            name='demo_steps',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.RunPython(update_demo_states),
    ]
