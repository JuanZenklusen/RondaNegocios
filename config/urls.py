"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuentas/", include("apps.accounts.urls")),
    path("", include("apps.notifications.urls")),
    path("", include("apps.registrations.urls")),
    path("", include("apps.accreditation.urls")),
    path("", include("apps.agenda.urls")),
    path("", include("apps.meetings.urls")),
    path("", include("apps.events.urls")),
    path("", include("apps.networking.urls")),
    path("", include("apps.companies.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
