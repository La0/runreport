from django.contrib import admin
from models import Athlete, UserCategory
from payments.admin import PaymentTransactionInline, PaymentEventInline

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
  inlines = (
    PaymentTransactionInline,
    PaymentEventInline,
  )
admin.site.register(Athlete, AthleteAdmin)

class UserCategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'code', 'min_year', 'max_year')
admin.site.register(UserCategory, UserCategoryAdmin)
