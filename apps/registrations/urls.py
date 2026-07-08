from django.urls import path

from . import views

app_name = "registrations"

urlpatterns = [
    path("eventos/<int:pk>/inscribirme/", views.RegisterToEventView.as_view(), name="register"),
    path("mis-inscripciones/", views.MyRegistrationsView.as_view(), name="mine"),
    path("inscripciones/<int:pk>/cancelar/", views.CancelRegistrationView.as_view(), name="cancel"),
    # Organizador
    path(
        "gestion/eventos/<int:pk>/inscripciones/",
        views.EventRegistrationsView.as_view(),
        name="event_registrations",
    ),
    path(
        "gestion/inscripciones/<int:pk>/responder/",
        views.RespondRegistrationView.as_view(),
        name="respond",
    ),
]
