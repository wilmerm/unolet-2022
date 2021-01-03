from django.urls import path 

from . import views


urlpatterns = [
    path("item/create/", views.ItemCreateView.as_view(), name="inventory-item-create"),
    path("item/<int:pk>/update/", views.ItemUpdateView.as_view(), name="inventory-item-update"),
]