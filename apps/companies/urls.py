from django.urls import path

from . import views

app_name = "companies"

urlpatterns = [
    path("mi-empresa/", views.CompanyProfileEditView.as_view(), name="profile_edit"),
    path("empresa/<slug:slug>/", views.CompanyPublicDetailView.as_view(), name="public_detail"),
]
