from django.urls import path

from . import views

app_name = "meetings"

urlpatterns = [
    path("eventos/<slug:slug>/ronda/", views.RoundView.as_view(), name="round"),
    path(
        "eventos/<slug:slug>/ronda/solicitar/",
        views.RequestMeetingView.as_view(),
        name="request",
    ),
    path(
        "ronda/solicitudes/<int:pk>/responder/",
        views.RespondMeetingRequestView.as_view(),
        name="respond",
    ),
    path(
        "ronda/reuniones/<int:pk>/cancelar/",
        views.CancelMeetingView.as_view(),
        name="cancel",
    ),
]
