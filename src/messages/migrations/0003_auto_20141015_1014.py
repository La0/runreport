# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('messages', '0002_message_private'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50, choices=[(b'mail', b'Mail'), (b'comments_public', b'Public comments'), (b'comments_private', b'Private comments')])),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='message',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='message',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='message',
            name='session',
        ),
        migrations.AddField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(related_name=b'messages', default=None, to='messages.Conversation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='writer',
            field=models.ForeignKey(related_name=b'messages_written', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
