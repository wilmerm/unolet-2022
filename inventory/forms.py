from django import forms 

from base.forms import ModelForm
from company.models import Company
from document.models import Document, DocumentType
from inventory.models import (Item, ItemFamily, ItemGroup, Movement)


class ItemForm(ModelForm):
    """Formulario para artículos."""

    class Meta:
        model = Item
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MovementForm(ModelForm):
    """Formulario para movimientos."""

    class Meta:
        model = Movement
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("-----", self.company.id)
        


    

