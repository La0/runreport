from django.contrib import admin
from models import *

class PlanSessionAdmin(admin.TabularInline):
  model = PlanSession

class PlanAdmin(admin.ModelAdmin):
  list_display = ('name', 'creator', 'created' )
  inlines = [PlanSessionAdmin, ]
admin.site.register(Plan, PlanAdmin)

