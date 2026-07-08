from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import forms, views

app_name = "accounts"

urlpatterns = [
    path("registro/", views.RegisterView.as_view(), name="register"),
    path("ingresar/", views.EmailLoginView.as_view(), name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.ProfileView.as_view(), name="profile"),
    # Recuperación de contraseña (flujo estándar de Django, templates propios).
    path(
        "recuperar/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset_form.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
            form_class=forms.StyledPasswordResetForm,
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "recuperar/enviado/",
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "recuperar/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            form_class=forms.StyledSetPasswordForm,
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "recuperar/listo/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
