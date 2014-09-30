# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('club', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clubmembership',
            name='trainers',
            field=models.ManyToManyField(related_name=b'trainees', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clubmembership',
            name='user',
            field=models.ForeignKey(related_name=b'memberships', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='clubmembership',
            unique_together=set([('user', 'club')]),
        ),
        migrations.AddField(
            model_name='clublink',
            name='club',
            field=models.ForeignKey(related_name=b'links', to='club.Club'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clubinvite',
            name='club',
            field=models.ForeignKey(related_name=b'invites', blank=True, to='club.Club', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clubinvite',
            name='sender',
            field=models.ForeignKey(related_name=b'inviter', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='clubinvite',
            unique_together=set([('recipient', 'type')]),
        ),
        migrations.AddField(
            model_name='club',
            name='main_trainer',
            field=models.ForeignKey(related_name=b'club_main_trainer', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='manager',
            field=models.ForeignKey(related_name=b'club_manager', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='club.ClubMembership'),
            preserve_default=True,
        ),
    ]
