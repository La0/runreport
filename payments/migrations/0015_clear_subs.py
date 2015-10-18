# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def remove_subs(apps, schema_editor):
    '''
    Remove all old PaymentSubscription
    '''
    PaymentSubscription = apps.get_model('payments', 'PaymentSubscription')
    PaymentSubscription.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0014_auto_20151009_1108'),
    ]

    operations = [
        migrations.RunPython(remove_subs),
    ]
