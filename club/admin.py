from django.contrib import admin
from models import *

class ClubMembershipAdmin(admin.TabularInline):
  model = ClubMembership

class ClubLinkAdmin(admin.TabularInline):
  model = ClubLink

class ClubInviteAdmin(admin.ModelAdmin):
  list_display = ('club', 'type', 'sender', 'slug', 'created')
admin.site.register(ClubInvite, ClubInviteAdmin)

class ClubAdmin(admin.ModelAdmin):
  list_display = ('name',)
  inlines = [ClubLinkAdmin, ClubMembershipAdmin, ]
admin.site.register(Club, ClubAdmin)
