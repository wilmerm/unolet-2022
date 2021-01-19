from django.urls import path 

from . import views


urlpatterns = [
    path("", views.Index.as_view(), name="inventory-index"),

    path("item/create/", views.ItemCreateView.as_view(), 
    name="inventory-item-create"),

    path("item/list/", views.ItemListView.as_view(), 
    name="inventory-item-list"),

    path("item/list/<int:pk>/update/", views.ItemUpdateView.as_view(), 
    name="inventory-item-update"),

    # Json views.

    path("json/item/list/", views.item_list_jsonview, 
    name="inventory-item-list-json"),

    path("json/movement/<int:document>/form/", views.movement_form_jsonview, 
    name="inventory-movement-form-json"),



]