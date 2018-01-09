from django.contrib import admin
from payments.models import PaymentPeriod, PaymentTransaction


class PaymentPeriodAdmin(admin.ModelAdmin):
    list_display = ('club', 'mangopay_id', 'created')


admin.site.register(PaymentPeriod, PaymentPeriodAdmin)


class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('club', 'created', 'status', 'mangopay_id')


admin.site.register(PaymentTransaction, PaymentTransactionAdmin)


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
