from django.shortcuts import render

from dal import autocomplete

from person.models import Person, IdentificationType


class PersonAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para Person."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        qs = Person.active_objects.filter(company=company_pk)

        if self.request.GET.get("q"):
            qs = qs.filter(tags__icontains=text.Text.get_tag(q))

        return qs


class IdentificationTypeAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para IdentificationType."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        qs = IdentificationType.objects.filter(company=company_pk)

        if self.request.GET.get("q"):
            qs = qs.filter(tags__icontains=text.Text.get_tag(q))

        return qs