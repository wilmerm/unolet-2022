from django import forms 
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from dal import autocomplete

from base.forms import ModelForm
from company.models import Company
from document.models import Document, DocumentType
from inventory.models import (Item, ItemFamily, ItemGroup, Movement)


class ItemGroupForm(ModelForm):
    """Formulario para grupos de artículos."""

    class Meta:
        model = ItemGroup
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ItemFamilyForm(ModelForm):
    """Formulario para familia de artículos."""

    class Meta:
        model = ItemFamily
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ItemForm(ModelForm):
    """Formulario para artículos."""

    class Meta:
        model = Item
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["group"] = forms.ModelChoiceField(label=_("Grupo"),
            queryset=ItemGroup.objects.filter(company=self.company), 
            widget=autocomplete.ModelSelect2(
            url=reverse("inventory-autocomplete-itemgroup", 
            kwargs={"company": self.company.pk})))

        self.fields["family"] = forms.ModelChoiceField(label=_("Familia"),
            queryset=ItemFamily.objects.filter(company=self.company), 
            widget=autocomplete.ModelSelect2(
            url=reverse("inventory-autocomplete-itemfamily", 
            kwargs={"company": self.company.pk})))

        self.fields["tax"] = forms.ModelChoiceField(label=_("Impuesto"),
            queryset=ItemFamily.objects.filter(company=self.company), 
            widget=autocomplete.ModelSelect2(
            url=reverse("finance-autocomplete-tax", 
            kwargs={"company": self.company.pk})))

class MovementForm(ModelForm):
    """Formulario para movimientos."""

    class Meta:
        model = Movement
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("-----", self.company.id)
        


    

