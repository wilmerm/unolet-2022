from django.urls import path
from . import views



urlpatterns = [
    path("warehouse/list/", views.WarehouseListView.as_view(), name="warehouse-warehouse-list"),
    path("warehouse/list/<int:warehouse>/", views.WarehouseDetailView.as_view(), name="warehouse-warehouse-detail"),
]