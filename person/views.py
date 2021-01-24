from django.shortcuts import render
from django.db.models import Sum, F

from dal import autocomplete

from unoletutils import views
from person.models import Person, IdentificationType
from person.forms import PersonForm


class PersonListView(views.ListView):
    """Listado de personas."""
    model = Person


class PersonDetailView(views.DetailView):
    """Detalle de una persona."""
    model = Person


class PersonCreateView(views.CreateView):
    """Crea una persona."""
    model = Person
    form_class = PersonForm


class PersonUpdateView(views.UpdateView):
    """Modifica una persona."""
    model = Person
    form_class = PersonForm


class PersonDeleteView(views.DeleteView):
    """Elimina una persona."""
    model = Person
    form_class = PersonForm


class IdentificationTypeUpdateView(views.UpdateView):
    """Actualiza un tipo de identificación."""
    model = IdentificationType


# django-autocomplete-light

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