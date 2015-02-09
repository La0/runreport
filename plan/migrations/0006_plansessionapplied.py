# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0009_remove_sportsession_plan_session'),
        ('plan', '0005_plan_start'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanSessionApplied',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'applied', max_length=20, choices=[(b'applied', 'Applied'), (b'done', 'Done'), (b'failed', 'Failed')])),
                ('validated', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('plan_session', models.ForeignKey(related_name=b'applications', to='plan.PlanSession')),
                ('sport_session', models.OneToOneField(related_name=b'plan_session', to='sport.SportSession')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
