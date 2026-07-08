from django.contrib import admin

from .models import Message, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "title", "level", "is_read", "created_at")
    list_filter = ("level", "is_read")
    search_fields = ("recipient__email", "title")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "created_at", "read_at")
    search_fields = ("sender__email", "recipient__email")
