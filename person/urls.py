from django.urls import path

from person import views


urlpatterns = [
    
    # django-autocomplete-light

    path("json/person/list", views.PersonAutocompleteView.as_view(),
    name="person-autocomplete-person"),

    path("json/identificationtype/list/", 
    views.IdentificationTypeAutocompleteView.as_view(), 
    name="person-autocomplete-identificationtype")
]