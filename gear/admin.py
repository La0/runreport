from django.contrib import admin
from models import GearCategory, GearBrand, GearItem


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
      'fields' : ('name', 'description'),
    }),
    ('Links', {
      'fields' : ('category', 'brand', 'user', 'sessions', ),
    }),
    ('Dates', {
      'fields' : ('start', 'end', ),
    }),
  )
  readonly_fields = ('sessions', )
admin.site.register(GearItem, GearItemAdmin)
