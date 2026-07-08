from django.contrib import admin

from .models import ActivityAttendance


@admin.register(ActivityAttendance)
class ActivityAttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "activity", "created_at")
    search_fields = ("user__email", "activity__title")
    list_filter = ("activity__event",)
