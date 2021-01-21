from django.urls import path 

from finance import views


urlpatterns = [

    path("", views.IndexView.as_view(), name="finance-index"),

    path("account/payable/", views.AccountPayableView.as_view(),
    name="finance-account-payable"),

    path("account/receivable/", views.AccountReceivableView.as_view(), 
    name="finance-account-receivable"),

    path("account/receivable/document/list/", 
    views.AccountReceivableDocumentListView.as_view(), 
    name="finance-account-receivable-document-list"),

    path("account/receivable/document/list/<int:pk>/", 
    views.AccountReceivableDocumentDetailView.as_view(),
    name="finance-account-receivable-document-detail"),

    # Json views.

    path("api/currency/detail/", views.currency_detail_jsonview, 
    name="api-finance-currency-detail"),

    # django-autocomplete-light 

    path("autocomplete/currency/list/", views.CurrencyAutocompleteView.as_view(),
    name="finance-autocomplete-currency"),
]