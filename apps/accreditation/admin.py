from django.contrib import admin

from .models import Accreditation, Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company", "cargo", "email")
    search_fields = ("first_name", "last_name", "company__razon_social")


@admin.register(Accreditation)
class AccreditationAdmin(admin.ModelAdmin):
    list_display = ("holder_name", "event", "status", "checked_in_at", "checked_out_at")
    search_fields = ("code", "participant__first_name", "participant__last_name")
    readonly_fields = ("code", "created_at")
