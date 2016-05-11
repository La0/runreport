# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0012_auto_20151015_1845'),
        ('payments', '0020_auto_20151026_1632'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nb_athletes', models.IntegerField(default=0)),
                ('nb_trainers', models.IntegerField(default=0)),
                ('nb_staff', models.IntegerField(default=0)),
                ('status', models.CharField(default=b'created', max_length=20, choices=[(b'free', 'Free'), (b'active', 'Active'), (b'paid', 'Paid'), (b'expired', 'Expired'), (b'error', 'Error')])),
                ('mangopay_id', models.CharField(max_length=50, unique=True, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('club', models.ForeignKey(related_name='periods', to='club.Club')),
            ],
        ),
        migrations.RemoveField(
            model_name='paymentsubscription',
            name='club',
        ),
        migrations.RemoveField(
            model_name='paymenttransaction',
            name='subscription',
        ),
        migrations.DeleteModel(
            name='PaymentSubscription',
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='period',
            field=models.ForeignKey(related_name='transactions', blank=True, to='payments.PaymentPeriod', null=True),
        ),
    ]
