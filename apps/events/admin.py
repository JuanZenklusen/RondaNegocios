from django.contrib import admin

from .models import Activity, Event, Table, TimeBlock


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0


class TableInline(admin.TabularInline):
    model = Table
    extra = 0


class TimeBlockInline(admin.TabularInline):
    model = TimeBlock
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "status", "start_date", "end_date", "organization")
    list_filter = ("status", "event_type", "modality", "organization")
    search_fields = ("name", "slug", "location")
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "start_date"
    inlines = [ActivityInline, TableInline, TimeBlockInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "activity_type", "start", "is_public")
    list_filter = ("activity_type", "is_public")
    search_fields = ("title", "event__name")
