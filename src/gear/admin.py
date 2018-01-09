from django.contrib import admin
from gear.models import GearCategory, GearBrand, GearItem


class GearCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'official', )


admin.site.register(GearCategory, GearCategoryAdmin)


class GearBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'official', )


admin.site.register(GearBrand, GearBrandAdmin)


class GearItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'user', )
    list_filter = ('brand', 'category', )
    fieldsets = (
        ('Base', {
            'fields': ('name', 'description'),
        }),
        ('Links', {
            'fields': ('category', 'brand', 'user', ),
        }),
        ('Dates', {
            'fields': ('start', 'end', ),
        }),
    )


admin.site.register(GearItem, GearItemAdmin)
