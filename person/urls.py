from django.urls import path

from person import views


urlpatterns = [
    path("person/create/", views.PersonCreateView.as_view(), 
    name="person-person-create"),

    path("person/list/", views.PersonListView.as_view(), 
    name="person-person-list"),

    path("person/list/<int:pk>/", views.PersonDetailView.as_view(), 
    name="person-person-detail"),

    path("person/list/<int:pk>/update/", views.PersonUpdateView.as_view(), 
    name="person-person-update"),

    path("person/list/<int:pk>/delete/", views.PersonDeleteView.as_view(), 
    name="person-person-delete"),

    path("identificationtype/<int:pk>/update/", 
    views.IdentificationTypeUpdateView.as_view(),
    name="person-identificationtype-update"),

    # django-autocomplete-light

    path("autocomplete/person/list", views.PersonAutocompleteView.as_view(),
    name="person-autocomplete-person"),

    path("autocomplete/identificationtype/list/", 
    views.IdentificationTypeAutocompleteView.as_view(), 
    name="person-autocomplete-identificationtype")
]