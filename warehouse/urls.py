from django.urls import path
from . import views



urlpatterns = [
    path("warehouse/create/", views.WarehouseCreateView.as_view(), 
    name="warehouse-warehouse-create"),

    path("warehouse/list/", views.WarehouseListView.as_view(), 
    name="warehouse-warehouse-list"),

    path("warehouse/list/<int:pk>/", views.WarehouseDetailView.as_view(), 
    name="warehouse-warehouse-detail"),

    path("warehouse/list/<int:pk>/update/", views.WarehouseUpdateView.as_view(), 
    name="warehouse-warehouse-update"),

    path("warehouse/list/<int:pk>/delete/", views.WarehouseDeleteView.as_view(), 
    name="warehouse-warehouse-delete"),

    # django-autocomplete-light

    path("json/warehouse/list/", views.WarehouseAutocompleteView.as_view(),
    name="warehouse-autocomplete-warehouse"),
    
]