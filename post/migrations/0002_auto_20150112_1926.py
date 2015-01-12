# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=25, choices=[(b'image source', 'Source Image'), (b'image thumb', 'Thumbnail Image')])),
                ('size', models.IntegerField()),
                ('width', models.IntegerField(null=True, blank=True)),
                ('height', models.IntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(related_name=b'children', to='post.PostMedia', null=True)),
                ('post', models.ForeignKey(related_name=b'medias', to='post.Post')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='post',
            name='html',
            field=models.TextField(verbose_name='Post content'),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(verbose_name='Name in the url'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Post title'),
        ),
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.CharField(max_length=15, verbose_name='Post Type', choices=[(b'race', 'Race'), (b'training', 'Training'), (b'blog', 'Blog')]),
        ),
    ]
