from django.contrib import admin
from apps.channel.models import *
from base.admin import BaseAdmin


@admin.register(Ticket)
class TicketAdmin(BaseAdmin):
    list_display = ['user', 'subject', 'description', 'status', 'created_at', 'updated_at']
    search_fields = ['user', 'subject', 'description', 'status', 'created_at', 'updated_at']
    list_filter = (
        'status',
    )
    fields = ['user', 'subject', 'description', 'status']


@admin.register(Message)
class MessageAdmin(BaseAdmin):
    list_display = ['ticket', 'user', 'content', 'timestamp']
    search_fields = ['ticket', 'user', 'content', 'timestamp']
