from django.contrib import admin
from models import *


class BadgeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )


admin.site.register(BadgeCategory, BadgeCategoryAdmin)


class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'position', )
    list_filter = ('category', )


admin.site.register(Badge, BadgeAdmin)
