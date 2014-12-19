# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0007_auto_20141219_1048'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('published', models.BooleanField(default=False)),
                ('type', models.CharField(max_length=15, choices=[(b'race', 'Race'), (b'training', 'Training'), (b'blog', 'Blog')])),
                ('title', models.CharField(max_length=255)),
                ('html', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('revision', models.IntegerField(default=1)),
                ('sessions', models.ManyToManyField(related_name=b'posts', to='sport.SportSession')),
                ('writer', models.ForeignKey(related_name=b'posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='post',
            unique_together=set([('writer', 'slug')]),
        ),
    ]
