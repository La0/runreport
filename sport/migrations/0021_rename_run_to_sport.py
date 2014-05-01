# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
      db.rename_table(u'run_runreport', u'sport_week')
      db.rename_table(u'run_runsession', u'sport_day')
      db.rename_table(u'run_garminactivity', u'garmin_activity')
      db.rename_table(u'run_sport', u'sport_list')
      db.rename_table(u'run_racecategory', u'sport_race_category')

    def backwards(self, orm):
      db.rename_table(u'sport_week', u'run_runreport')
      db.rename_table(u'sport_day', u'run_runsession')
      db.rename_table(u'garmin_activity', u'run_garminactivity')
      db.rename_table(u'sport_list', u'run_sport')
      db.rename_table(u'sport_race_category', u'run_racecategory',)

    models = {
        
    }

    complete_apps = ['sport']
