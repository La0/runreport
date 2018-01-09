from django.contrib import admin
from users.models import Athlete, UserCategory


class AthleteAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username',
        'first_name', 'last_name',
        'is_staff',
    )
    search_fields = (
        'email',
        'username',
        'first_name', 'last_name',
    )


admin.site.register(Athlete, AthleteAdmin)


class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'min_year', 'max_year')


admin.site.register(UserCategory, UserCategoryAdmin)
