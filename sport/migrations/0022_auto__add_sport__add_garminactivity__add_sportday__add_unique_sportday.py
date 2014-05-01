# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sport'
        db.create_table('sport_list', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sport.Sport'], null=True)),
            ('depth', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('sport', ['Sport'])

        # Adding model 'GarminActivity'
        db.create_table('garmin_activity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('garmin_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(related_name='garmin_activities', to=orm['sport.SportDay'])),
            ('sport', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sport.Sport'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Athlete'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('distance', self.gf('django.db.models.fields.FloatField')()),
            ('speed', self.gf('django.db.models.fields.TimeField')()),
            ('md5_raw', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('md5_laps', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('md5_details', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('sport', ['GarminActivity'])

        # Adding model 'SportDay'
        db.create_table('sport_day', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sessions', to=orm['sport.SportWeek'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('distance', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='training', max_length=12)),
            ('sport', self.gf('django.db.models.fields.CharField')(default='running', max_length=20)),
            ('plan_session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['plan.PlanSession'], null=True, blank=True)),
            ('race_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sport.RaceCategory'], null=True, blank=True)),
        ))
        db.send_create_signal('sport', ['SportDay'])

        # Adding unique constraint on 'SportDay', fields ['report', 'date']
        db.create_unique('sport_day', ['report_id', 'date'])

        # Adding model 'RaceCategory'
        db.create_table('sport_race_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('distance', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('sport', ['RaceCategory'])

        # Adding model 'SportWeek'
        db.create_table('sport_week', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Athlete'])),
            ('year', self.gf('django.db.models.fields.IntegerField')(default=2013)),
            ('week', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('distance', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('task', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('plan_week', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['plan.PlanWeek'], null=True, blank=True)),
        ))
        db.send_create_signal('sport', ['SportWeek'])

        # Adding unique constraint on 'SportWeek', fields ['user', 'year', 'week']
        db.create_unique('sport_week', ['user_id', 'year', 'week'])


    def backwards(self, orm):
        # Removing unique constraint on 'SportWeek', fields ['user', 'year', 'week']
        db.delete_unique('sport_week', ['user_id', 'year', 'week'])

        # Removing unique constraint on 'SportDay', fields ['report', 'date']
        db.delete_unique('sport_day', ['report_id', 'date'])

        # Deleting model 'Sport'
        db.delete_table('sport_list')

        # Deleting model 'GarminActivity'
        db.delete_table('garmin_activity')

        # Deleting model 'SportDay'
        db.delete_table('sport_day')

        # Deleting model 'RaceCategory'
        db.delete_table('sport_race_category')

        # Deleting model 'SportWeek'
        db.delete_table('sport_week')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'plan.plan': {
            'Meta': {'unique_together': "(('creator', 'slug'),)", 'object_name': 'Plan'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Athlete']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            'task': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'plan.plansession': {
            'Meta': {'unique_together': "(('week', 'day'),)", 'object_name': 'PlanSession'},
            'day': ('django.db.models.fields.IntegerField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'week': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sessions'", 'to': u"orm['plan.PlanWeek']"})
        },
        u'plan.planweek': {
            'Meta': {'unique_together': "(('plan', 'order'),)", 'object_name': 'PlanWeek'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'weeks'", 'to': u"orm['plan.Plan']"})
        },
        'sport.garminactivity': {
            'Meta': {'object_name': 'GarminActivity', 'db_table': "'garmin_activity'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {}),
            'garmin_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5_details': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'md5_laps': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'md5_raw': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'garmin_activities'", 'to': "orm['sport.SportDay']"}),
            'speed': ('django.db.models.fields.TimeField', [], {}),
            'sport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sport.Sport']"}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Athlete']"})
        },
        'sport.racecategory': {
            'Meta': {'object_name': 'RaceCategory', 'db_table': "'sport_race_category'"},
            'distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'sport.sport': {
            'Meta': {'object_name': 'Sport', 'db_table': "'sport_list'"},
            'depth': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sport.Sport']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'sport.sportday': {
            'Meta': {'unique_together': "(('report', 'date'),)", 'object_name': 'SportDay', 'db_table': "'sport_day'"},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'plan_session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['plan.PlanSession']", 'null': 'True', 'blank': 'True'}),
            'race_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sport.RaceCategory']", 'null': 'True', 'blank': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sessions'", 'to': "orm['sport.SportWeek']"}),
            'sport': ('django.db.models.fields.CharField', [], {'default': "'running'", 'max_length': '20'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'training'", 'max_length': '12'})
        },
        'sport.sportweek': {
            'Meta': {'unique_together': "(('user', 'year', 'week'),)", 'object_name': 'SportWeek', 'db_table': "'sport_week'"},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan_week': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['plan.PlanWeek']", 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Athlete']"}),
            'week': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '2013'})
        },
        u'users.athlete': {
            'Meta': {'object_name': 'Athlete'},
            'auto_send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.UserCategory']", 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'frequency_rest': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'garmin_login': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'garmin_password': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'nb_sessions': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'vma': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'users.usercategory': {
            'Meta': {'object_name': 'UserCategory'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_year': ('django.db.models.fields.IntegerField', [], {}),
            'min_year': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        }
    }

    complete_apps = ['sport']