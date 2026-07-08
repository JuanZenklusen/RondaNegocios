from django.urls import path

from . import views

app_name = "networking"

urlpatterns = [
    path("red/", views.DirectoryView.as_view(), name="directory"),
    path("red/favoritos/", views.FavoritesView.as_view(), name="favorites"),
    path("red/conexiones/", views.ConnectionsView.as_view(), name="connections"),
    path("red/<int:pk>/favorito/", views.ToggleFavoriteView.as_view(), name="toggle_favorite"),
    path("red/<int:pk>/conectar/", views.ConnectView.as_view(), name="connect"),
    path(
        "red/conexiones/<int:pk>/responder/",
        views.RespondConnectionView.as_view(),
        name="respond_connection",
    ),
]
