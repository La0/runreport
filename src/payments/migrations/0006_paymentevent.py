# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0005_remove_paymentsubscription_end'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_id', models.CharField(unique=True, max_length=32)),
                ('type', models.CharField(max_length=50)),
                ('raw_data', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('subscription', models.ForeignKey(related_name='events', blank=True, to='payments.PaymentSubscription', null=True)),
                ('user', models.ForeignKey(related_name='payment_events', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
