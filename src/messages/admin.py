from django.contrib import admin
from messages.models import *


class MessageAdmin(admin.ModelAdmin):
    list_display = ('writer', 'conversation', 'created')


admin.site.register(Message, MessageAdmin)
