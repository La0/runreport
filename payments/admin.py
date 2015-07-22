from django.contrib import admin
from models import PaymentEvent, PaymentSubscription, PaymentTransaction

class PaymentEventAdmin(admin.ModelAdmin):
  list_display = ('event_id', 'type', 'user', 'subscription', 'transaction', 'created', 'applied')
admin.site.register(PaymentEvent, PaymentEventAdmin)

class PaymentSubscriptionAdmin(admin.ModelAdmin):
  list_display = ('user', 'offer', 'paymill_id', 'created')
admin.site.register(PaymentSubscription, PaymentSubscriptionAdmin)

class PaymentTransactionAdmin(admin.ModelAdmin):
  list_display = ('user', 'created', 'paymill_id', 'amount')
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)

# Inlines used from users admin
class PaymentSubscriptionInline(admin.TabularInline):
  model = PaymentSubscription
  extra = 0

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

