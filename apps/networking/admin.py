from django.contrib import admin

from .models import ConnectionRequest, Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("owner", "company", "created_at")
    search_fields = ("owner__razon_social", "company__razon_social")


@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ("from_company", "to_company", "status", "created_at", "responded_at")
    list_filter = ("status",)
    search_fields = ("from_company__razon_social", "to_company__razon_social")
