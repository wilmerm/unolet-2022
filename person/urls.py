from django.urls import path

from person import views


urlpatterns = [
    path("person/<int:pk>/", views.PersonDetailView.as_view(), 
    name="person-person-detail"),

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