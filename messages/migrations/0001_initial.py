# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0002_auto_20140930_1320'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('revision', models.IntegerField(default=1)),
                ('recipient', models.ForeignKey(related_name=b'messages_received', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name=b'messages_sent', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(related_name=b'comments', blank=True, to='sport.SportSession', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
