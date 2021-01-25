from django.urls import path 

from . import views


urlpatterns = [
    path("", views.Index.as_view(), name="inventory-index"),

    # Item.

    path("item/create/", views.ItemCreateView.as_view(), 
    name="inventory-item-create"),

    path("item/list/", views.ItemListView.as_view(), 
    name="inventory-item-list"),

    path("item/list/<int:pk>/", views.ItemDetailView.as_view(), 
    name="inventory-item-detail"),

    path("item/list/<int:pk>/update/", views.ItemUpdateView.as_view(), 
    name="inventory-item-update"),

    path("item/list/<int:item>/movements/", views.ItemMovementListView.as_view(), 
    name="inventory-item-movement-list"),

    # ItemGroup.

    path("itemgroup/create/" ,views.ItemGroupCreateView.as_view(),
    name="inventory-itemgroup-create"),

    path("itemgroup/list/", views.ItemGroupListView.as_view(), 
    name="inventory-itemgroup-list"),

    path("itemgroup/list/<int:pk>/", views.ItemGroupDetailView.as_view(), 
    name="inventory-itemgroup-detail"),

    path("itemgroup/list/<int:pk>/update/", views.ItemGroupUpdateView.as_view(), 
    name="inventory-itemgroup-update"),

    # ItemFamily.

    path("itemfamily/create/" ,views.ItemFamilyCreateView.as_view(),
    name="inventory-itemfamily-create"),

    path("itemfamily/list/", views.ItemFamilyListView.as_view(), 
    name="inventory-itemfamily-list"),

    path("itemfamily/list/<int:pk>/", views.ItemFamilyDetailView.as_view(), 
    name="inventory-itemfamily-detail"),

    path("itemfamily/list/<int:pk>/update/", views.ItemFamilyUpdateView.as_view(), 
    name="inventory-itemfamily-update"),

    # Movement.

    path("movement/list/<int:pk>/", views.MovementDetailView.as_view(),
    name="inventory-movement-detail"),

    # Json views.

    path("api/item/list/", views.item_list_jsonview, 
    name="api-inventory-item-list"),

    path("api/movement/<int:document>/form/", views.movement_form_jsonview, 
    name="api-inventory-movement-form"),

    path("api/movement/<int:document>/delete/", views.movement_delete_jsonview,
    name="api-inventory-movement-delete"),

]