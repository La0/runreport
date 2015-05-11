from django.contrib import admin
from payments.models import PaymentOffer


class PaymentOfferAdmin(admin.ModelAdmin):
  list_display = ('name', 'interval', 'amount', 'currency')
admin.site.register(PaymentOffer, PaymentOfferAdmin)
