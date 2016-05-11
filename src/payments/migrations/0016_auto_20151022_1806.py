# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0012_auto_20151015_1845'),
        ('payments', '0015_auto_20151014_1539'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentevent',
            name='subscription',
        ),
        migrations.RemoveField(
            model_name='paymentevent',
            name='transaction',
        ),
        migrations.RemoveField(
            model_name='paymentevent',
            name='user',
        ),
        migrations.RemoveField(
            model_name='paymenttransaction',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='paymenttransaction',
            name='paymill_id',
        ),
        migrations.RemoveField(
            model_name='paymenttransaction',
            name='user',
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='club',
            field=models.ForeignKey(related_name='transactions', default=1, to='club.Club'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='mangopay_id',
            field=models.CharField(default='', unique=True, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='response',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='status',
            field=models.CharField(default=b'open', max_length=20, choices=[(b'CREATED', 'Created'), (b'FAILED', 'Failed'), (b'SUCEEDED', 'Succeeded')]),
        ),
        migrations.DeleteModel(
            name='PaymentEvent',
        ),
    ]
