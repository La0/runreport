from django.contrib import admin
from models import *

class UserCategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'code', 'min_year', 'max_year')
admin.site.register(UserCategory, UserCategoryAdmin)
