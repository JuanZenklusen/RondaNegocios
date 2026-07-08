from django.urls import path

from . import views

app_name = "agenda"

urlpatterns = [
    path(
        "eventos/<slug:slug>/mi-agenda/",
        views.MyEventAgendaView.as_view(),
        name="event_agenda",
    ),
    path(
        "eventos/<slug:slug>/mi-agenda/actividad/<int:pk>/asistir/",
        views.ToggleActivityAttendanceView.as_view(),
        name="toggle_activity",
    ),
]
