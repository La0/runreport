from django.contrib import admin
from page.models import *


class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created', 'user')


admin.site.register(Page, PageAdmin)
