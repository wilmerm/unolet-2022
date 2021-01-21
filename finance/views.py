from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, F, When, Case
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from dal import autocomplete

from unoletutils.libs import text
from unoletutils import views
from document.models import Document, DocumentType
from finance.models import Currency


class IndexView(views.TemplateView):
    """Página principal de la aplicación finance."""
    template_name = "finance/index.html"


class AccountPayableView(views.TemplateView):
    """Cuenta por pagar."""
    template_name = "finance/account_payable.html"


class AccountReceivableView(views.TemplateView):
    """Cuenta por cobrar."""
    template_name = "finance/account_receivable.html"


class AccountReceivableDocumentListView(views.ListView):
    """Listado de documentos pendients de pago."""
    model = Document
    template_name = "finance/account_receivable_document_list.html"
    title = _l("Documentos pendientes de pago")

    def get_queryset(self):
        qs = Document.accept_payments_objects.all() # Docs que aceptan pagos.
        qs = qs.annotate(payments=Sum("transaction__amount"))
        qs = qs.annotate(balance=F("total")-F("payments"))
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


class CurrencyAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para Currency."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        qs = Currency.objects.filter(company=company_pk)

        if self.request.GET.get("q"):
            qs = qs.filter(tags__icontains=text.Text.get_tag(q))

        return qs