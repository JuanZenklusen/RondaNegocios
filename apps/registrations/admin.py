from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "status", "payment_status", "amount", "created_at")
    list_filter = ("status", "payment_status", "event")
    search_fields = ("event__name", "user__email")
    readonly_fields = ("created_at", "decided_at")
    autocomplete_fields = ("event", "user")
