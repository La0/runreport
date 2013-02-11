from django.contrib import admin
from models import *

class RunSessionAdmin(admin.TabularInline):
  model = RunSession
  max_num = 7

class RunReportAdmin(admin.ModelAdmin):
  list_display = ('user', 'week',)
  list_filter = ('user', )
  inlines = [RunSessionAdmin, ]
admin.site.register(RunReport, RunReportAdmin)

