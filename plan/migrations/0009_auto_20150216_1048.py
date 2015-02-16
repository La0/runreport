# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plan', '0008_auto_20150213_1138'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanApplied',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('plan', models.ForeignKey(related_name=b'applications', to='plan.Plan')),
                ('user', models.ForeignKey(related_name=b'plans_applied', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='planapplied',
            unique_together=set([('user', 'plan')]),
        ),
        migrations.AddField(
            model_name='plansessionapplied',
            name='application',
            field=models.ForeignKey(related_name=b'sessions', null=True, to='plan.PlanApplied'),
            preserve_default=False,
        ),
    ]
