from django.contrib import admin
from club.models import *
from payments.admin import PaymentTransactionInline


class ClubMembershipAdmin(admin.TabularInline):
    model = ClubMembership


class ClubLinkAdmin(admin.TabularInline):
    model = ClubLink


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', '_has_full_access')
    inlines = []
    inlines = (
        PaymentTransactionInline,
        ClubMembershipAdmin,
        ClubLinkAdmin,
    )


admin.site.register(Club, ClubAdmin)
