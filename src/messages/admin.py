from django.contrib import admin
from models import *


class MessageAdmin(admin.ModelAdmin):
    list_display = ('writer', 'conversation', 'created')


admin.site.register(Message, MessageAdmin)
