# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [(b'gear', '0001_initial'), (b'gear', '0002_auto_20150925_1031'), (b'gear', '0003_auto_20150925_2358'), (b'gear', '0004_auto_20150926_1047'), (b'gear', '0005_remove_gearitem_sessions')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sport', '0016_auto_20150722_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='GearBrand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('official', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='GearCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('official', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='GearItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('start', models.DateTimeField(null=True, blank=True)),
                ('end', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('brand', models.ForeignKey(related_name='items', to='gear.GearBrand')),
                ('category', models.ForeignKey(related_name='items', to='gear.GearCategory')),
                ('sessions', models.ManyToManyField(to=b'sport.SportSession', blank=True)),
                ('sports', models.ManyToManyField(to=b'sport.Sport', blank=True)),
                ('user', models.ForeignKey(related_name='items', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='gearbrand',
            name='owner',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gearcategory',
            name='owner',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='gearbrand',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='gearcategory',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='gearitem',
            options={'ordering': ('user', 'category', 'brand', 'created')},
        ),
        migrations.AlterField(
            model_name='gearitem',
            name='brand',
            field=models.ForeignKey(related_name='items', verbose_name='Brand', to='gear.GearBrand'),
        ),
        migrations.AlterField(
            model_name='gearitem',
            name='category',
            field=models.ForeignKey(related_name='items', verbose_name='Category', to='gear.GearCategory'),
        ),
        migrations.AlterField(
            model_name='gearitem',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='gearitem',
            name='end',
            field=models.DateTimeField(null=True, verbose_name='End usage date', blank=True),
        ),
        migrations.AlterField(
            model_name='gearitem',
            name='name',
            field=models.CharField(max_length=250, verbose_name='Equipment name'),
        ),
        migrations.AlterField(
            model_name='gearitem',
            name='sports',
            field=models.ManyToManyField(to=b'sport.Sport', verbose_name='Default sports', blank=True),
        ),
        migrations.AlterField(
            model_name='gearitem',
            name='start',
            field=models.DateTimeField(null=True, verbose_name='Start usage date', blank=True),
        ),
        migrations.RemoveField(
            model_name='gearitem',
            name='sessions',
        ),
    ]
