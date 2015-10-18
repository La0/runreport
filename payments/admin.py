from django.contrib import admin
from models import PaymentEvent, PaymentSubscription, PaymentTransaction

class PaymentEventAdmin(admin.ModelAdmin):
  list_display = ('event_id', 'type', 'subscription', 'transaction', 'created', 'applied')
admin.site.register(PaymentEvent, PaymentEventAdmin)

class PaymentSubscriptionAdmin(admin.ModelAdmin):
  list_display = ('club', 'mangopay_id', 'created')
admin.site.register(PaymentSubscription, PaymentSubscriptionAdmin)

class PaymentTransactionAdmin(admin.ModelAdmin):
  list_display = ('created', 'paymill_id', 'amount')
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)

class PaymentTransactionInline(admin.TabularInline):
  model = PaymentTransaction
  extra = 0

class PaymentEventInline(admin.TabularInline):
  model = PaymentEvent
  extra = 0
  fields = (
    'event_id',
    'type',
    'applied',
  )

