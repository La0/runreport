# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0015_clear_subs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentoffer',
            name='clubs',
        ),
        migrations.AddField(
            model_name='paymentsubscription',
            name='mangopay_id',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paymentsubscription',
            name='nb_athletes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='paymentsubscription',
            name='club',
            field=models.ForeignKey(related_name='subscriptions', to='club.Club'),
        ),
        migrations.AlterField(
            model_name='paymentsubscription',
            name='end',
            field=models.DateTimeField(),
        ),
        migrations.AlterUniqueTogether(
            name='paymentsubscription',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='paymentsubscription',
            name='offer',
        ),
        migrations.RemoveField(
            model_name='paymentsubscription',
            name='paymill_id',
        ),
        migrations.DeleteModel(
            name='PaymentOffer',
        ),
    ]
