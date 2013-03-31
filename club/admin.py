from django.contrib import admin
from models import *

class ClubMembershipAdmin(admin.TabularInline):
  model = ClubMembership

class ClubAdmin(admin.ModelAdmin):
  list_display = ('name',)
  inlines = [ClubMembershipAdmin, ]
admin.site.register(Club, ClubAdmin)
