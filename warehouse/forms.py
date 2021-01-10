
from django import forms 

from base.forms import ModelForm
from warehouse.models import Warehouse


class WarehouseForm(ModelForm):
    """Formulario para creación y modificación de almacenes."""

    class Meta:
        model = Warehouse
        fields = "__all__"

    