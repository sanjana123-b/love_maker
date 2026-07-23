from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'match', 'content', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp']
