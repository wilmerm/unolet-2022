from django.shortcuts import render
from django.views.generic import (DetailView, UpdateView, CreateView, ListView)
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from dal import autocomplete

from unoletutils.libs import text
from unoletutils.views import (UpdateView, CreateView, ListView, DetailView, 
    DeleteView, TemplateView)
from document.models import (Document, DocumentType)
from document.forms import (DocumentForm, DocumentPurchaseForm, 
    DocumentInvoiceForm, DocumentInventoryInputForm, 
    DocumentInventoryOutputForm)


class Index(TemplateView):
    """Página principal de la app document."""
    template_name = "document/index.html"
    title = _l("Documentos")


class BaseDocument:
    model = Document
    generictype = None


class DocumentListView(BaseDocument, ListView):
    TITLES = {
        None: _l("Documentos"),
        DocumentType.TRANSFER: _l("Transferencias de inventario"),
        DocumentType.INVENTORY_INPUT: _l("Entradas de inventario"),
        DocumentType.INVENTORY_OUTPUT: _l("Salidas de inventario"),
        DocumentType.PURCHASE: _l("Compras"),
        DocumentType.INVOICE: _l("Facturas"),
        DocumentType.INVOICE_RETURN: _l("Devoluciónes de facturas")
    }
    title = TITLES[None]

    model = Document
    template_name = "document/document_list.html"

    LIST_DISPLAY_DICT = {
        None: (
            ("get_number", _l("Número")),
            ("create_date", _l("Fecha")),
            ("warehouse", _l("Almacén")),
        ),
        DocumentType.TRANSFER: (
            ("get_number", _l("Número")),
            ("create_date", _l("Fecha")),
            ("warehouse", _l("Almacén")),
            ("transfer_warehouse", _l("Almacén de transferencia")),
        ),
        DocumentType.INVENTORY_INPUT: (
            ("get_number", _l("Número")),
            ("create_date", _l("Fecha")),
            ("warehouse", _l("Almacén")),
            ("get_person_name", _l("Suplidor")),
        ),
        DocumentType.INVENTORY_OUTPUT: (
            ("get_number", _l("Número")),
            ("create_date", _l("Fecha")),
            ("warehouse", _l("Almacén")),
            ("get_person_name", _l("Suplidor")),
        ),
        DocumentType.PURCHASE: (
            ("get_number", _l("Número")),
            ("create_date", _l("Fecha")),
            ("warehouse", _l("Almacén")),
            ("get_person_name", _l("Suplidor")),
            ("amount", _l("Importe")),
            ("discount", _l("Descuento")),
            ("tax", _l("Impuesto")),
            ("total", _l("Total")),
            ("get_balance", _l("Balance")),
        ),
    }

    list_display = LIST_DISPLAY_DICT[None]

    list_display_links = ("get_number",)

    list_display_cssclass = {
        "amount": "text-end intcomma",
        "discount": "text-end intcomma",
        "tax": "text-end intcomma",
        "total": "text-end intcomma",
    }

    generictype = None

    def __setup(self, **kwargs):
        generictype = kwargs.get("generictype", self.generictype)
        self.title = self.TITLES[generictype]
        self.queryset = Document.objects.filter(doctype__generic_type=generictype)
        self.list_display = self.LIST_DISPLAY_DICT[generictype]
        self.template_name = f"document/document/{generictype}_list.html"

    def dispatch(self, request, *args, **kwargs):
        # El tipo genérico de los documentos a mostrar está pasado en la url.
        # Aquí filtramos el queryset para solo esos tipos.
        self.__setup(**kwargs)
        return super().dispatch(request, *args, **kwargs)


class DocumentUpdateView(BaseDocument, UpdateView):
    """Modifica un documento."""
    model = Document
    form_class = DocumentForm
    company_field = "doctype__company"
    generictype = None


class DocumentCreateView(BaseDocument, CreateView):
    """Crea un documento."""
    model = Document
    form_class = DocumentForm
    generictype = None

    def get_template_names(self):
        if self.generictype:
            return f"document/document/{self.generictype}_form.html"
        return super().get_template_names()

    def get_form_class(self):
        if self.generictype:
            class_name = f"Document{self.generictype.capitalize()}Form"
            return globals()[class_name]
        return super().get_form_class()
        


class DocumentTypeAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para DocumentType."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        qs = DocumentType.active_objects.filter(company=company_pk)

        if self.request.GET.get("q"):
            qs = qs.filter(tags__icontains=text.Text.get_tag(q))

        return qs