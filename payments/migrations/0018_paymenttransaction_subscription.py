# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0017_auto_20151022_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenttransaction',
            name='subscription',
            field=models.ForeignKey(related_name='transactions', blank=True, to='payments.PaymentSubscription', null=True),
        ),
    ]
