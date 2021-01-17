from django.shortcuts import render, get_object_or_404
from django.views.generic import (DetailView, UpdateView, CreateView, ListView)
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.http import JsonResponse, Http404
from django.db.models import Sum, F
from django.core import serializers

from dal import autocomplete

from unoletutils.libs import text
from unoletutils.views import (UpdateView, CreateView, ListView, DetailView, 
    DeleteView, TemplateView)
from company.models import Company
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
        "get_balance": "text-end intcomma",
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

    def get_template_names(self):
        if self.generictype:
            return f"document/document/{self.generictype}_form.html"
        return super().get_template_names()

    def get_form_class(self):
        if self.generictype:
            generic = "".join([e.title() for e in self.generictype.split("_")])
            class_name = f"Document{generic}Form"
            return globals()[class_name]
        return super().get_form_class()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["generictype"] = getattr(self, "generictype", None)
        return kwargs


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
            generic = "".join([e.title() for e in self.generictype.split("_")])
            class_name = f"Document{generic}Form"
            return globals()[class_name]
        return super().get_form_class()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["generictype"] = getattr(self, "generictype", None)
        return kwargs
        

class DocumentTypeAutocompleteView(autocomplete.Select2QuerySetView):
    """Vista dal.autocomplete para DocumentType."""

    def get_queryset(self):
        company_pk = self.kwargs["company"]
        generictype = self.kwargs["generictype"]

        qs = DocumentType.active_objects.filter(
            company=company_pk, generic_type=generictype)

        if self.request.GET.get("q"):
            qs = qs.filter(tags__icontains=text.Text.get_tag(q))

        return qs


# Json Views.

def document_movements_jsonview(request, company: int, 
    document: int) -> JsonResponse:
    """Retorna un listado de movimientos del documento en cuestión."""

    company = get_object_or_404(Company, pk=company)
    document = get_object_or_404(Document, pk=document)

    if not company.user_has_access(request.user):
        raise Http404("El usuario no tiene acceso a esta empresa.")

    if company != document.doctype.company:
        raise Http404(f"El documento {document} no pertenece a esta empresa.")

    movement_qs = document.get_movements().annotate(
        amount=F("quantity") * F("price") - F("discount"), 
        total=F("amount") + F("tax"))

    doctype = document.doctype
    tax_receipt = getattr(doctype, "tax_receipt", None)

    out = {
        "document": {
            "id": document.id,
            "warehouse": str(document.warehouse),
            "warehouse_id": document.warehouse_id,
            "warehouse__name": document.warehouse.name,
            "warehouse__is_active": document.warehouse.is_active,
            "transfer_warehouse": str(document.transfer_warehouse),
            "transfer_warehouse_id": document.transfer_warehouse_id,
            "transfer_warehouse__name": getattr(document.transfer_warehouse, "name", ""),
            "transfer_warehouse__is_active": getattr(document.transfer_warehouse, "is_active", ""),
            "number": document.number,
            "person": str(document.person),
            "person_id": document.person_id,
            "currency": str(document.currency),
            "currency_id": document.currency_id,
            "currency_rate": document.currency_rate,
            "tax_receipt_number": str(document.tax_receipt_number),
            "tax_receipt_number_id": document.tax_receipt_number_id,
            "pay_taxes": document.pay_taxes,
            "amount": document.amount,
            "discount": document.discount,
            "tax": document.tax,
            "total": document.total,
            "create_user": str(document.create_user),
            "create_date": document.create_date,
            "doctype": str(document.doctype),
            "doctype_id": document.doctype.id,
            "doctype__code": doctype.code,
            "doctype__name": doctype.name,
            "doctype__generic_type": doctype.generic_type,
            "doctype__affect_cost": doctype.affect_cost,
            "doctype__is_active": doctype.is_active,
            "doctype__tax_receipt_id": getattr(tax_receipt, "id", None),
            "doctype__tax_receipt__code": getattr(tax_receipt, "code", None),
            "doctype__tax_receipt__name": getattr(tax_receipt, "name", None),
            "doctype__tax_receipt__is_active": getattr(tax_receipt, "is_active", False),
        },
        "movements": list(movement_qs.values("id", "number", "item_id",
            "item__codename", "item__name", "name", "quantity", "price",
            "discount", "tax", "amount", "total")
        ),
        "totals": {
            "count": movement_qs.count(),
            "discount": movement_qs.aggregate(s=Sum("discount"))["s"] or 0,
            "tax": movement_qs.aggregate(s=Sum("tax"))["s"] or 0,
            "amount": movement_qs.aggregate(s=Sum("amount"))["s"] or 0,
            "total": movement_qs.aggregate(s=Sum("total"))["s"] or 0,
        },

    }

    return JsonResponse({"data": out})