from django.contrib import admin
from models import PaymentEvent, PaymentSubscription, PaymentTransaction, PaymentOffer

class PaymentOfferAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug', 'target', 'amount', )
admin.site.register(PaymentOffer, PaymentOfferAdmin)

class PaymentEventAdmin(admin.ModelAdmin):
  list_display = ('event_id', 'type', 'subscription', 'transaction', 'created', 'applied')
admin.site.register(PaymentEvent, PaymentEventAdmin)

class PaymentSubscriptionAdmin(admin.ModelAdmin):
  list_display = ('club', 'offer', 'paymill_id', 'created')
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

