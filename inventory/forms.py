from django import forms 
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from dal import autocomplete

from base.forms import ModelForm, SearchForm
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


class ItemSearchForm(SearchForm):
    """Formulario de búsqueda para artículos."""

    available_json__available__gt = forms.BooleanField(required=False, 
    label=_l("Solo disponibles"))

    def clean(self):
        available__gt = self.cleaned_data["available_json__available__gt"]
        if available__gt in (True, 1, "on", "true", "True", "1"):
            self.cleaned_data["available_json__available__gt"] = 0
        else:
            self.cleaned_data["available_json__available__gt"] = -99999999999999999


class MovementForm(ModelForm):
    """Formulario para movimientos."""

    class Meta:
        model = Movement
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

class MovementSearchForm(SearchForm):
    """Formulario de búsqueda de movimientos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item__tags_icontains"] = self.fields.pop("tags__icontains")
    
