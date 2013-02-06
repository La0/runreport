from django.contrib import admin
from models import *

class RunReportAdmin(admin.ModelAdmin):
  pass
admin.site.register(RunReport, RunReportAdmin)

class RunSessionAdmin(admin.ModelAdmin):
  pass
admin.site.register(RunSession, RunSessionAdmin)
