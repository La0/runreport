from django.contrib import admin
from models import *

class AthleteAdmin(admin.ModelAdmin):
  list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'category', 'garmin_login')
admin.site.register(Athlete, AthleteAdmin)

class UserCategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'code', 'min_year', 'max_year')
admin.site.register(UserCategory, UserCategoryAdmin)
