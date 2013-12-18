from django.contrib import admin
from models import *

class PlanWeekAdmin(admin.TabularInline):
  model = PlanWeek

class PlanAdmin(admin.ModelAdmin):
  list_display = ('name', 'creator', 'created' )
  inlines = [PlanWeekAdmin, ]
admin.site.register(Plan, PlanAdmin)

