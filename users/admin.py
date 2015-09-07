from django.contrib import admin
from models import Athlete, UserCategory
from payments.admin import PaymentSubscriptionInline, PaymentTransactionInline, PaymentEventInline

class AthleteAdmin(admin.ModelAdmin):
  list_display = (
    'email', 'username',
    'first_name', 'last_name',
    '_is_premium',
    'is_staff',
  )
  search_fields = (
    'email',
    'username',
    'first_name', 'last_name',
  )
  inlines = (
    PaymentSubscriptionInline,
    PaymentTransactionInline,
    PaymentEventInline,
  )
admin.site.register(Athlete, AthleteAdmin)

class UserCategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'code', 'min_year', 'max_year')
admin.site.register(UserCategory, UserCategoryAdmin)
