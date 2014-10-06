# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(blank=True)),
                ('name', models.CharField(max_length=255)),
                ('markdown', models.TextField(null=True, blank=True)),
                ('html', models.TextField(null=True, blank=True)),
                ('type', models.CharField(max_length=12, choices=[(b'help', b'Help'), (b'news', b'News')])),
                ('published', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
