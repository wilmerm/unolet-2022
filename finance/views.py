from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from dal import autocomplete

from unoletutils.libs import text
from unoletutils import views
from finance.models import Currency


class AccountPayableView(views.TemplateView):
    """Cuenta por pagar."""
    template_name = "finance/account_payable.html"


class AccountReceivableView(views.TemplateView):
    """Cuenta por cobrar."""
    template_name = "finance/account_receivable.html"


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