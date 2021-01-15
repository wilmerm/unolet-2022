from django.shortcuts import render

from dal import autocomplete

from unoletutils.libs import text
from finance.models import Currency


class CurrencyAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para Currency."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        qs = Currency.objects.filter(company=company_pk)

        if self.request.GET.get("q"):
            qs = qs.filter(tags__icontains=text.Text.get_tag(q))

        return qs