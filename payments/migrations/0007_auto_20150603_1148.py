# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_paymentevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paymill_id', models.CharField(max_length=50, null=True, blank=True)),
                ('amount', models.FloatField()),
                ('currency', models.CharField(max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='paymentsubscription',
            name='paymill_transaction_id',
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='subscription',
            field=models.ForeignKey(related_name='transactions', to='payments.PaymentSubscription'),
        ),
        migrations.AddField(
            model_name='paymentevent',
            name='transaction',
            field=models.ForeignKey(related_name='events', blank=True, to='payments.PaymentTransaction', null=True),
        ),
    ]
