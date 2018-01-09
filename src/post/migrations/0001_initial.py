# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-09 13:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('messages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(verbose_name='Name in the url')),
                ('published', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('race', 'Race'), ('training', 'Training'), ('blog', 'Blog')], max_length=15, verbose_name='Post Type')),
                ('title', models.CharField(max_length=255, verbose_name='Post title')),
                ('html', models.TextField(verbose_name='Post content')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('revision', models.IntegerField(default=1)),
                ('conversation', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post', to='messages.Conversation')),
            ],
        ),
        migrations.CreateModel(
            name='PostMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('image source', 'Source Image'), ('image thumb', 'Thumbnail Image'), ('image crop', 'Cropped Image')], max_length=25)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('size', models.IntegerField()),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='post.PostMedia')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medias', to='post.Post')),
            ],
        ),
    ]
