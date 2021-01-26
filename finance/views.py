from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, F, Value, When, Case
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from dal import autocomplete

from unoletutils.libs import text
from unoletutils import views
from document.models import Document, DocumentType
from person.models import Person
from finance.models import (Currency, Transaction)
from finance.forms import TransactionForm


class IndexView(views.TemplateView):
    """Página principal de la aplicación finance."""
    template_name = "finance/index.html"


class TransactionCreateView(views.CreateView):
    """Crea una transacción."""
    model = Transaction
    form_class = TransactionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["document"] = get_object_or_404(Document, 
            doctype__company=self.kwargs["company"], pk=self.kwargs["document"])
        return kwargs


class TransactionDetailView(views.DetailView):
    """Detalle de una transacción."""
    model = Transaction
    company_field = "document__doctype__company"


class AccountPayableView(views.TemplateView):
    """Cuenta por pagar."""
    template_name = "finance/account_payable.html"


class AccountReceivableView(views.TemplateView):
    """Cuenta por cobrar."""
    template_name = "finance/account_receivable.html"


class AccountReceivablePersonBalanceListView(views.ListView):
    """Listado de personas con balance pendiente de pago."""
    model = Person
    template_name = "finance/account_receivable_person_list.html"
    title = _l("Personas con balance pendiente de pago")

    def get_queryset(self):
        qs = Person.objects.all()
        # Solo los tipos de doc. que afectan la cuenta por cobrar.
        types = DocumentType.TYPES_THAT_CAN_AFFECT_THE_ACCOUNT_RECEIVABLE
        qs = qs.annotate(
            total=Sum(Case(When(document__doctype__generic__in=types, 
                then=F("document__total")))),
            payments=Sum(Case(When(document__doctype__generic__in=types,
                then=F("document__transaction__amount")))),
            balance=F("total")-F("payments"),
            available=F("credit_limit")-F("balance")
        )
        self.totals = qs.aggregate(
            Sum("credit_limit"), 
            Sum("available"),
            Sum("total"),
            Sum("payments"),
            Sum("balance"),
        )
        return qs


class AccountReceivablePersonBalanceDetailView(views.DetailView):
    """Detalle del balance de una persona y sus facturas pendientes de pago."""
    model = Person
    template_name = "finance/account_receivable_person_detail.html"
    
    def get_title(self):
        return "%s %s" % (_("Balance pendiente para"), self.get_object())


class AccountReceivableDocumentListView(views.ListView):
    """Listado de documentos pendientes de pago."""
    model = Document
    template_name = "finance/account_receivable_document_list.html"
    title = _l("Documentos pendientes de pago")

    def get_queryset(self):
        qs = Document.accept_payments_objects.all() # Docs que aceptan pagos.
        qs = qs.annotate(payments=Sum("transaction__amount"))
        qs = qs.annotate(balance=F("total")-F("payments"))
        self.totals = qs.aggregate(Sum("total"), Sum("payments"), Sum("balance"))
        return qs


class AccountReceivableDocumentDetailView(views.DetailView):
    """Detalle un documento pendiente de pago."""
    model = Document
    template_name = "finance/account_receivable_document_detail.html"
    company_field = "doctype__company"
    
    def get_title(self):
        return "%s %s" % (_l("Pagos realizados al documento"), self.object)


# Json Views.

def currency_detail_jsonview(request, company):
    """Obtiene el detalle de la moneda con el 'id' pasado por URL."""
    currency = get_object_or_404(Currency, 
        company=company, pk=request.GET.get("id"))

    data = {"code": currency.code, "symbol": currency.symbol, 
        "name": currency.name, "rate": currency.rate, 
        "is_default": currency.is_default}

    return JsonResponse({"data": data})


# django-autocomplete-light

class CurrencyAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para Currency."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        qs = Currency.objects.filter(company=company_pk)
        if self.request.GET.get("q"):
            qs = qs.filter(tags__icontains=text.Text.get_tag(q))
        return qs


class TaxAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para Tax."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        qs = Tax.objects.filter(company=company_pk)
        if self.request.GET.get("q"):
            qs = qs.filter(tags__icontains=text.Text.get_tag(q))
        return qs