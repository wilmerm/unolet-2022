from django.urls import path, include
from . import views


urlpatterns = [
    path("company/<int:company>/", views.CompanyDetailView.as_view(), name="company-company-detail"),
    path("company/<int:company>/warehouse/", include("warehouse.urls")),
    path("company/<int:company>/document/", include("document.urls")),
    path("company/<int:company>/inventory/", include("inventory.urls")),
    path("company/<int:company>/person/", include("person.urls")),
    path("company/<int:company>/finance/", include("finance.urls")),
]