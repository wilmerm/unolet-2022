from django.urls import path 

from finance import views


urlpatterns = [

    path("", views.IndexView.as_view(), name="finance-index"),

    # Transaction.

    path("transaction/<int:document>/create/", 
    views.TransactionCreateView.as_view(), 
    name="finance-transaction-create"),

    path("transaction/<int:document>/<int:pk>/",
    views.TransactionDetailView.as_view(), 
    name="finance-transaction-detail"),

    # Account paypable.

    path("account/payable/", views.AccountPayableView.as_view(),
    name="finance-account-payable"),

    # Account receivable.

    path("account/receivable/", views.AccountReceivableView.as_view(), 
    name="finance-account-receivable"),

    path("account/receivable/person/list/", 
    views.AccountReceivablePersonBalanceListView.as_view(), 
    name="finance-account-receivable-person-list"),

    path("account/receivable/person/list/<int:pk>/",
    views.AccountReceivablePersonBalanceDetailView.as_view(),
    name="finance-account-receivable-person-detail"),

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

    path("autocomplete/tax/list/", views.TaxAutocompleteView.as_view(),
    name="finance-autocomplete-tax"),
]