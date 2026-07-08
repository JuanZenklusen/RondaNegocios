from django.contrib import admin

from .models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("company_a", "company_b", "score", "organization", "updated_at")
    list_filter = ("organization",)
    search_fields = ("company_a__razon_social", "company_b__razon_social")
    readonly_fields = ("updated_at",)
