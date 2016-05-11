# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_auto_20150511_1731'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentsubscription',
            old_name='paymill_subscription_id',
            new_name='paymill_transaction_id',
        ),
        migrations.AlterUniqueTogether(
            name='paymentsubscription',
            unique_together=set([('user', 'offer')]),
        ),
    ]
