# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0008_auto_20150726_2000'),
        ('payments', '0012_auto_20150724_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentoffer',
            name='clubs',
            field=models.ManyToManyField(related_name='offers', through='payments.PaymentSubscription', to='club.Club'),
        ),
        migrations.AddField(
            model_name='paymentsubscription',
            name='club',
            field=models.ForeignKey(related_name='subscriptions', blank=True, to='club.Club', null=True),
        ),
        migrations.AlterField(
            model_name='paymentsubscription',
            name='user',
            field=models.ForeignKey(related_name='subscriptions', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='paymentsubscription',
            unique_together=set([('user', 'offer'), ('club', 'offer')]),
        ),
    ]
