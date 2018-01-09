# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-09 13:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('mail', 'Mail'), ('comments_public', 'Public comments'), ('comments_private', 'Private comments'), ('comments_week', 'Week comments'), ('plan_session', 'Plan session'), ('post', 'Post')], max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('revision', models.IntegerField(default=1)),
                ('conversation', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='messages.Conversation')),
            ],
        ),
    ]
