from django.db import models
from django.db.models import Sum, F
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.core.validators import (MinValueValidator, MaxValueValidator)
from django.urls import reverse_lazy

from unoletutils.libs import utils


def get_default_currency():
    """Obtiene la moneda marcada como predeterminada."""
    from finance.models import Currency
    return Currency.objects.filter(is_default=True).last()


class DocumentType(utils.ModelBase):
    """
    Tipo de documento.
    """

    INVOICE = "invoice"
    PURCHASE = "purchase"
    PURCHASE_ORDER = "purchase_order"
    QUOTATION = "quotation"
    INVENTORY_INPUT = "inventory_input"
    INVENTORY_OUTPUT = "inventory_output"
    GENERIC_TYPE_CHOICES = (
        (INVOICE, _l("Factura")),
        (PURCHASE, _l("Compra")),
        (PURCHASE_ORDER, _l("Orden de compra")),
        (QUOTATION, _l("Cotización")),
        (INVENTORY_INPUT, _l("Entrada de inventario")),
        (INVENTORY_OUTPUT, _l("Salida de inventario")),
    )

    INPUT, OUTPUT = "input", "output"
    INVENTORY_CHOICES = (
        (INPUT, _l("Entrada")),
        (OUTPUT, _l("Salida")),
    )

    CREDIT, DEBIT = "credit", "debit"
    ACCOUNT_CHOICES = (
        (CREDIT, _l("Crédito")),
        (DEBIT, _l("Débito")),
    )

    code = models.CharField(_l("código"), max_length=6)

    name = models.CharField(_l("nombre"), max_length=70)

    generic_type = models.CharField(_l("tipo genérico"), max_length=20, 
    choices=GENERIC_TYPE_CHOICES, 
    help_text=_l("tipo genérico al que pertenece."))

    inventory = models.CharField(_l("inventario"), max_length=10, blank=True,
    choices=INVENTORY_CHOICES, help_text=_l("indica de que forma será "
    "afectado el inventario de artículos cuando se use este tipo de documento."))

    tax_receipt = models.ForeignKey("finance.TaxReceipt", blank=True, null=True,
    on_delete=models.PROTECT, verbose_name=_l("comprobante fiscal"))

    affect_cost = models.BooleanField(_l("afecta el costo"), default=False, 
    help_text=_l("indica si el costo promedio de los artículos será calculado."))

    is_active = models.BooleanField(_l("activo"), default=True)

    class Meta:
        verbose_name = _l("tipo de documento")
        verbose_name_plural = _l("tipos de documentos")
        constraints = [
            models.UniqueConstraint(fields=("company", "code"), 
                name="unique_company_documenttype")
        ]

    def __str__(self):
        return self.code
    
    def clean(self):
        self.code = " ".join(self.code.split()).upper()
        
        if DocumentType.objects.filter(company=self.company).exclude(pk=self.pk):
            raise ValidationError({"code", 
                _("Ya existe otro tipo de documento con este código.")})

    def save(self, *args, **kwargs):
        self.code = " ".join(self.code.split()).upper()
        return super().save(*args, **kwargs)


class InputDocumentManager(models.Manager):
    """
    Manejador solo para documentos que afectan el inventario como entrada.
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            doctype__inventory=DocumentType.INPUT)


class OutputDocumentManager(models.Manager):
    """
    Manejador solo para documentos que afectan el inventario como salida.
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            doctype__inventory=DocumentType.OUTPUT)


class Document(utils.ModelBase):
    """
    Documento.
    """

    company = None # La empresa será doctype.company

    warehouse = models.ForeignKey("warehouse.Warehouse", 
    on_delete=models.CASCADE)

    doctype = models.ForeignKey(DocumentType, on_delete=models.PROTECT,
    verbose_name=_l("tipo"))

    number = models.IntegerField(_l("número"), editable=False)

    person = models.ForeignKey("person.Person", on_delete=models.PROTECT, 
    null=True, blank=True)

    person_name = models.CharField(_l("nombre de la persona"), max_length=100,
    blank=True)

    note = models.CharField(_l("nota"), max_length=500, blank=True)

    currency = models.ForeignKey("finance.Currency", on_delete=models.PROTECT,
    default=get_default_currency, null=True, verbose_name=_l("moneda"))

    currency_rate = models.DecimalField(_l("tasa de cambio"), max_digits=10, 
    decimal_places=2, default=1, blank=True, null=True,
    validators=[MinValueValidator(0)])

    tax_receipt_number = models.OneToOneField("finance.TaxReceiptNumber", 
    on_delete=models.PROTECT, editable=False, blank=True, null=True,
    verbose_name=_("Número de comprobante fiscal"))

    # Campos para consultas.

    amount = models.DecimalField(_l("importe"), max_digits=32, decimal_places=2,
    null=True, blank=True, editable=False)

    discount = models.DecimalField(_l("descuento"), max_digits=32, 
    decimal_places=2, null=True, blank=True, editable=False)

    tax = models.DecimalField(_l("impuesto"), max_digits=32, 
    decimal_places=2, null=True, blank=True, editable=False)

    total = models.DecimalField(_l("total"), max_digits=32, 
    decimal_places=2, null=True, blank=True, editable=False)

    # Seguimiento.

    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, 
    on_delete=models.PROTECT, null=True, blank=True)

    create_date = models.DateTimeField(_l("fecha de creación"), 
    auto_now_add=True)

    objects = models.Manager()
    input_document_objects = InputDocumentManager()
    output_document_objects = OutputDocumentManager()

    class Meta:
        verbose_name = _l("documento")
        verbose_name_plural = _l("documentos")
        constraints = [
            models.UniqueConstraint(fields=("doctype", "number"), 
                name="unique_doctype_number")
        ]

    def __str__(self):
        if self.pk:
            return "{}-{:0>12}".format(self.doctype, self.number)
        return "%s %s" % (_("Nuevo"), self._meta.verbose_name)
    
    def get_next_number_for_type(self, doctype=None):
        """Obtiene el siguiente número para el tipo de documento indicado."""
        try:
            mx = Document.objects.filter(doctype=doctype).order_by("number")[0]
        except (IndexError):
            return 1

        return mx.number + 1

    def get_absolute_url(self):
        return reverse_lazy("document-document-update", 
            kwargs={"company": self.doctype.company.pk, "pk": self.pk})

    def clean(self):
        if not self.pk:
            self.number = self.get_next_number_for_type(self.doctype)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.number = self.get_next_number_for_type(self.doctype)
        
        if self.currency_rate == None:
            self.currency_rate = self.currency.rate or 1
        return super().save(*args, **kwargs)

    def calculate(self):
        """
        Calcula los totales, actualiza los campos correspondientes y retorna 
        un diccionario con los resultados.
        """
        movements = self.movement_set.all()
        out = {"amount": 0, "discount": 0, "tax": 0, "total": 0, 
            "movements": movements, "updated": False}
        out["amount"] = movements.aggregate(s=Sum(F("quantity") * F("price")))["s"]
        out["discount"] = movements.aggregate(s=Sum("discount"))["s"]
        out["tax"] = movements.aggregate(s=Sum("tax"))["s"]
        out["total"] = movements.aggregate(s=Sum(
            ((F("quantity") * F("price")) - F("discount")) + F("tax") ))["s"]


        # for movement in movements:
        #     out["amount"] += movement.get_amount()
        #     out["discount"] += movement.discount
        #     out["tax"] += movement.tax
        #     out["total"] += movement.get_total()

        # Actualizamos los campos si exiten diferencias.
        if ((out["amount"] != self.amount) or (out["discount"] != self.discount)
            or (out["tax"] != self.tax) or (out["total"] != self.total)):
            self.amount = out["amount"]
            self.discount = out["discount"]
            self.tax = out["tax"]
            self.total = out["total"]
            self.save_without_historical_record()
            out["updated"] = True

        return out