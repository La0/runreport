from django.contrib import admin
from models import *

class PaymentEventAdmin(admin.ModelAdmin):
  list_display = ('event_id', 'type', 'user', 'subscription', 'created')
admin.site.register(PaymentEvent, PaymentEventAdmin)

