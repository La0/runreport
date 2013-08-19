# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClubInvite'
        db.create_table('club_clubinvite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='inviter', to=orm['auth.User'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invitee', null=True, to=orm['auth.User'])),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='invites', null=True, to=orm['club.Club'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('used', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('club', ['ClubInvite'])

        # Adding field 'Club.max_staff'
        db.add_column('club_club', 'max_staff',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Club.max_trainer'
        db.add_column('club_club', 'max_trainer',
                      self.gf('django.db.models.fields.IntegerField')(default=2),
                      keep_default=False)

        # Adding field 'Club.max_athlete'
        db.add_column('club_club', 'max_athlete',
                      self.gf('django.db.models.fields.IntegerField')(default=20),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ClubInvite'
        db.delete_table('club_clubinvite')

        # Deleting field 'Club.max_staff'
        db.delete_column('club_club', 'max_staff')

        # Deleting field 'Club.max_trainer'
        db.delete_column('club_club', 'max_trainer')

        # Deleting field 'Club.max_athlete'
        db.delete_column('club_club', 'max_athlete')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'club.club': {
            'Meta': {'object_name': 'Club'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_trainer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'club_main_trainer'", 'null': 'True', 'to': "orm['auth.User']"}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'club_manager'", 'to': "orm['auth.User']"}),
            'max_athlete': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            'max_staff': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'max_trainer': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['club.ClubMembership']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'club.clubinvite': {
            'Meta': {'object_name': 'ClubInvite'},
            'club': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'invites'", 'null': 'True', 'to': "orm['club.Club']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitee'", 'null': 'True', 'to': "orm['auth.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'inviter'", 'to': "orm['auth.User']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'used': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'club.clublink': {
            'Meta': {'object_name': 'ClubLink'},
            'club': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['club.Club']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '250'})
        },
        'club.clubmembership': {
            'Meta': {'unique_together': "(('user', 'club'),)", 'object_name': 'ClubMembership'},
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['club.Club']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'trainers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'trainees'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships'", 'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['club']