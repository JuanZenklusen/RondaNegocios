from django.contrib import admin

from .models import Company, Need, Product, Rubro, Service


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0


class NeedInline(admin.TabularInline):
    model = Need
    extra = 0


@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "cuit", "rubro", "organization", "is_public")
    list_filter = ("is_public", "rubro", "organization", "province")
    search_fields = ("razon_social", "nombre_fantasia", "cuit", "slug")
    prepopulated_fields = {"slug": ("razon_social",)}
    autocomplete_fields = ("rubro",)
    inlines = [ProductInline, ServiceInline, NeedInline]
    readonly_fields = ("created_at", "updated_at")
