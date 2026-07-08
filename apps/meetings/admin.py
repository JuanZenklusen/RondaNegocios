from django.contrib import admin

from .models import Meeting, MeetingRequest


@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ("event", "from_company", "to_company", "time_block", "status")
    list_filter = ("status", "event")
    search_fields = ("from_company__razon_social", "to_company__razon_social")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("event", "company_a", "company_b", "time_block", "table", "status")
    list_filter = ("status", "event")
    search_fields = ("company_a__razon_social", "company_b__razon_social")
