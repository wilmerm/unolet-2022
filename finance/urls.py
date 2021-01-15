from django.urls import path 

from finance import views


urlpatterns = [


    # django-autocomplete-light 

    path("json/currency/list/", views.CurrencyAutocompleteView.as_view(),
    name="finance-autocomplete-currency"),
]