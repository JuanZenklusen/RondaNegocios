from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("notificaciones/", views.NotificationsView.as_view(), name="list"),
    path("notificaciones/<int:pk>/abrir/", views.OpenNotificationView.as_view(), name="open"),
    path("notificaciones/leer-todas/", views.MarkAllReadView.as_view(), name="mark_all_read"),
    path("mensajes/", views.InboxView.as_view(), name="inbox"),
    path("mensajes/<int:user_pk>/", views.ConversationView.as_view(), name="conversation"),
    path("mensajes/<int:user_pk>/enviar/", views.SendMessageView.as_view(), name="send"),
]
