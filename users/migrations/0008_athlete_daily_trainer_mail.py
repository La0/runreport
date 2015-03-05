# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20150114_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='daily_trainer_mail',
            field=models.BooleanField(default=True, verbose_name='Daily trainer mail'),
            preserve_default=True,
        ),
    ]
