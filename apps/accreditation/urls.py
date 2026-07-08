from django.urls import path

from . import views

app_name = "accreditation"

urlpatterns = [
    path("credenciales/", views.CredentialsView.as_view(), name="credentials"),
    path("credencial/<str:code>/", views.CredentialDetailView.as_view(), name="credential"),
    path("credencial/<str:code>/qr.png", views.QRView.as_view(), name="qr"),
    path("representantes/nuevo/", views.ParticipantCreateView.as_view(), name="participant_create"),
    path(
        "representantes/<int:pk>/eliminar/",
        views.ParticipantDeleteView.as_view(),
        name="participant_delete",
    ),
    path(
        "inscripcion/<int:registration_pk>/acreditar/",
        views.AccreditParticipantView.as_view(),
        name="accredit",
    ),
    # Organizador
    path("gestion/acreditacion/<str:code>/", views.CheckInView.as_view(), name="checkin"),
    path(
        "gestion/eventos/<int:pk>/acreditaciones/",
        views.EventAccreditationsView.as_view(),
        name="event_accreditations",
    ),
]
