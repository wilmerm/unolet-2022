from django.shortcuts import render
from django.views.generic import (ListView, DetailView)
from django.shortcuts import get_object_or_404

#from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin

from unoletutils.libs.utils import view_decorator
from .models import Warehouse


@view_decorator()
class WarehouseListView(ListView):
    """Listado de almacenes de la empresa actual."""
    model = Warehouse

    def get_queryset(self):
        company = self.request.company
        qs = company.get_warehouse_list()
        return qs
    

@view_decorator(pk_in_url="warehouse")
class WarehouseDetailView(DetailView):
    """Detalle de un almacén."""
    model = Warehouse
    company_permission_required = "warehouse.view_warehouse"
    
    def get_object(self, queryset=None):
        return get_object_or_404(self.model, company=self.kwargs.get("company"), 
            pk=self.kwargs.get("warehouse"))