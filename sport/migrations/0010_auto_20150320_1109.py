# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def migrate_comment(app, schema_editor):
  '''
  Migrate SportWeek direct comment
  into conversations
  '''
  from messages.models import TYPE_COMMENTS_WEEK
  SportWeek = app.get_model('sport', 'SportWeek')
  Conversation = app.get_model('messages', 'Conversation')

  weeks = SportWeek.objects.filter(comment__isnull=False).exclude(comment='')
  for week in weeks:
    # Create a conversation
    conv = Conversation.objects.create(type=TYPE_COMMENTS_WEEK, session_user_id=week.user_id)

    # Attach it to the week
    week.conversation = conv
    week.save()

    # Create a new message with original comment
    m = conv.messages.create(writer_id=week.user_id, message=week.comment)
    m.created = week.updated # Use week last update date
    m.save()

class Migration(migrations.Migration):

    dependencies = [
        ('messages', '0007_auto_20150224_1558'),
        ('sport', '0009_remove_sportsession_plan_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportweek',
            name='conversation',
            field=models.OneToOneField(blank=True, to='messages.Conversation', null=True),
            preserve_default=True,
        ),
        migrations.RunPython(migrate_comment),
        migrations.RemoveField(
            model_name='sportweek',
            name='comment',
        ),
    ]
