# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gear', '0002_auto_20150925_1031'),
    ]

    operations = [
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
            field=models.ManyToManyField(to='sport.Sport', verbose_name='Default sports', blank=True),
        ),
        migrations.AlterField(
            model_name='gearitem',
            name='start',
            field=models.DateTimeField(null=True, verbose_name='Start usage date', blank=True),
        ),
    ]
