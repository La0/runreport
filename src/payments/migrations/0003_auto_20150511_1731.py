# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0002_auto_20150511_1306'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=False)),
                ('end', models.DateTimeField()),
                ('paymill_id', models.CharField(max_length=50)),
                ('paymill_subscription_id', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('offer', models.ForeignKey(related_name='subscriptions', to='payments.PaymentOffer')),
                ('user', models.ForeignKey(related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='paymentoffer',
            name='clients',
            field=models.ManyToManyField(related_name='offers', through='payments.PaymentSubscription', to=settings.AUTH_USER_MODEL),
        ),
    ]
