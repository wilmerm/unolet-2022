from django import forms
from django.urls import reverse_lazy

from dal import autocomplete

from base.forms import ModelForm
from warehouse.models import Warehouse
from document.models import (Document, DocumentType)
from person.models import Person
from finance.models import Currency


class DocumentForm(ModelForm):
    """Formulario para documentos."""

    class Meta:
        model = Document
        exclude = ["create_user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        warehouse_qs = Warehouse.active_objects.filter(company=self.company.pk)
        doctype_qs = DocumentType.active_objects.filter(company=self.company.pk)
        person_qs = Person.active_objects.filter(company=self.company.pk)
        currency_qs = Currency.objects.filter(company=self.company.pk)

        self.fields["warehouse"] = forms.ModelChoiceField(
            queryset=warehouse_qs, 
            widget=autocomplete.ModelSelect2(
                url=reverse_lazy("warehouse-autocomplete-warehouse", 
                kwargs={"company": self.company.pk})))

        self.fields["transfer_warehouse"] = forms.ModelChoiceField(
            queryset=warehouse_qs, 
            widget=autocomplete.ModelSelect2(
                url=reverse_lazy("warehouse-autocomplete-warehouse", 
                kwargs={"company": self.company.pk})))

        self.fields["doctype"] = forms.ModelChoiceField(
            queryset=doctype_qs, 
            widget=autocomplete.ModelSelect2(
                url=reverse_lazy("document-autocomplete-documenttype", 
                kwargs={"company": self.company.pk})))

        self.fields["person"] = forms.ModelChoiceField(
            queryset=person_qs, 
            widget=autocomplete.ModelSelect2(
                url=reverse_lazy("person-autocomplete-person", 
                kwargs={"company": self.company.pk})))

        self.fields["currency"] = forms.ModelChoiceField(
            queryset=currency_qs, 
            widget=autocomplete.ModelSelect2(
                url=reverse_lazy("finance-autocomplete-currency", 
                kwargs={"company": self.company.pk})))

        self.fields["note"].widget = forms.Textarea()


class DocumentPurchaseForm(DocumentForm):
    """Formulario para documentos de compra."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("transfer_warehouse")


class DocumentInvoiceForm(DocumentForm):
    """Formulario para facturas."""


class DocumentInventoryInputForm(DocumentForm):
    """Formulario para entradas de inventario."""


class DocumentInventoryOutputForm(DocumentForm):
    """Formulario para salidas de inventario."""

    

