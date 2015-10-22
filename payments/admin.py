from django.contrib import admin
from models import PaymentSubscription, PaymentTransaction

class PaymentSubscriptionAdmin(admin.ModelAdmin):
  list_display = ('club', 'mangopay_id', 'created')
admin.site.register(PaymentSubscription, PaymentSubscriptionAdmin)

class PaymentTransactionAdmin(admin.ModelAdmin):
  list_display = ('club', 'created', 'status', 'mangopay_id')
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)

class PaymentTransactionInline(admin.TabularInline):
  model = PaymentTransaction
  extra = 0
