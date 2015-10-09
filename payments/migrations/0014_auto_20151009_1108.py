# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0013_auto_20150726_2000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentoffer',
            name='clients',
        ),
        migrations.AlterUniqueTogether(
            name='paymentsubscription',
            unique_together=set([('club', 'offer')]),
        ),
        migrations.RemoveField(
            model_name='paymentsubscription',
            name='user',
        ),
    ]
