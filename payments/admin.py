from django.contrib import admin
from models import *

class PaymentEventAdmin(admin.ModelAdmin):
  list_display = ('event_id', 'type', 'user', 'subscription', 'transaction', 'created', 'applied')
admin.site.register(PaymentEvent, PaymentEventAdmin)

class PaymentSubscriptionAdmin(admin.ModelAdmin):
  list_display = ('user', 'offer', 'paymill_id', 'created')
admin.site.register(PaymentSubscription, PaymentSubscriptionAdmin)

class PaymentTransactionAdmin(admin.ModelAdmin):
  list_display = ('user', 'created', 'paymill_id', 'amount')
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)

