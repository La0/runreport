# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0021_auto_20151026_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentperiod',
            name='level',
            field=models.CharField(default=b'free', max_length=20, choices=[(b'free', b'Free'), (b'premium_s', 'Premium Small - 9,90\u20ac'), (b'premium_m', 'Premium Medium - 19,90\u20ac'), (b'premium_l', 'Premium Large - 49,90\u20ac')]),
        ),
        migrations.AlterField(
            model_name='paymentperiod',
            name='status',
            field=models.CharField(default=b'active', max_length=20, choices=[(b'active', 'Active'), (b'paid', 'Paid'), (b'expired', 'Expired'), (b'error', 'Error')]),
        ),
    ]
