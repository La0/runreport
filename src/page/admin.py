from django.contrib import admin
from models import *

class PageAdmin(admin.ModelAdmin):
  list_display = ('name', 'type', 'created', 'user')
admin.site.register(Page, PageAdmin)
