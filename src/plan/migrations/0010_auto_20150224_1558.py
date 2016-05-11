# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messages', '0007_auto_20150224_1558'),
        ('plan', '0009_auto_20150216_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='plansession',
            name='comments',
            field=models.OneToOneField(related_name=b'plan_session', null=True, blank=True, to='messages.Conversation'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='plansessionapplied',
            name='application',
            field=models.ForeignKey(related_name=b'sessions', to='plan.PlanApplied'),
        ),
    ]
