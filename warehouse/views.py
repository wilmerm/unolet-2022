from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from dal import autocomplete

from unoletutils.libs import text
from unoletutils.views import (ListView, DetailView, UpdateView, CreateView, 
    DeleteView, TemplateView)
from warehouse.models import Warehouse
from warehouse.forms import WarehouseForm


class WarehouseListView(ListView):
    """Listado de almacenes de la empresa actual."""
    model = Warehouse
    template_name = "warehouse/warehouse_list.html"
    paginate_by = 20
    list_display = (
        ("name", _l("nombre")),
        ("address", _l("address")),
    )

    def get_queryset(self):
        company = self.request.company
        self.queryset = company.get_warehouse_list()
        return super().get_queryset()
    

class WarehouseDetailView(DetailView):
    """Detalle de un almacén."""
    model = Warehouse
    company_permission_required = "warehouse.view_warehouse"

    def name(self):
        return "HOLA MUNDO"


class WarehouseCreateView(CreateView):
    """Crea un almacén."""
    model = Warehouse
    form_class = WarehouseForm
    #company_permission_required = "warehouse.add_warehouse"


class WarehouseUpdateView(UpdateView):
    """Modifica un almacén."""
    model = Warehouse
    form_class = WarehouseForm
    #company_permission_required = "warehouse.change_warehouse"


class WarehouseDeleteView(DeleteView):
    """Modifica un almacén."""
    model = Warehouse
    #company_permission_required = "warehouse.change_warehouse"


class WarehouseAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para Warehouse."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        qs = Warehouse.active_objects.filter(company=company_pk)
        q = self.request.GET.get("q")
        
        if q:
            q = text.Text.get_tag(q)
            qs = qs.filter(tags__icontains=q)

        return qs
