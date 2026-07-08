from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    # Gestión (organizador)
    path("gestion/eventos/", views.OrganizerEventListView.as_view(), name="list"),
    path("gestion/eventos/nuevo/", views.OrganizerEventCreateView.as_view(), name="create"),
    path(
        "gestion/eventos/<int:pk>/editar/", views.OrganizerEventUpdateView.as_view(), name="update"
    ),
    path(
        "gestion/eventos/<int:pk>/eliminar/",
        views.OrganizerEventDeleteView.as_view(),
        name="delete",
    ),
    # Público
    path("eventos/", views.PublicEventListView.as_view(), name="public_list"),
    path("eventos/<slug:slug>/", views.PublicEventDetailView.as_view(), name="public_detail"),
]
