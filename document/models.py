from django.db import models
from django.db.models import Sum, F
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from unoletutils.libs import utils
from finance.models import (Transaction)


def get_default_currency():
    """Obtiene la moneda marcada como predeterminada."""
    from finance.models import Currency
    return Currency.objects.filter(is_default=True).last()


class DocumentTypeActiveManager(models.Manager):
    """Obtiene los tipos de documentos activos."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class DocumentType(utils.ModelBase):
    """
    Tipo de documento.
    """

    INVOICE = "invoice"
    INVOICE_RETURN = "invoice_return"
    PURCHASE = "purchase"
    PURCHASE_ORDER = "purchase_order"
    QUOTATION = "quotation"
    INVENTORY_INPUT = "inventory_input"
    INVENTORY_OUTPUT = "inventory_output"
    TRANSFER = "transfer"
    ACCOUNTING_INCOME = "accounting_income"
    ACCOUNTING_EXPENSE = "accounting_expense"
    GENERIC_TYPE_CHOICES = (
        (INVOICE, _l("Factura")),
        (INVOICE_RETURN, _l("Devolución en factura")),
        (PURCHASE, _l("Compra")),
        (PURCHASE_ORDER, _l("Orden de compra")),
        (QUOTATION, _l("Cotización")),
        (INVENTORY_INPUT, _l("Entrada de inventario")),
        (INVENTORY_OUTPUT, _l("Salida de inventario")),
        (TRANSFER, _l("Transferencia de inventario")),
        (ACCOUNTING_INCOME, _l("Ingreso contable")),
        (ACCOUNTING_EXPENSE, _l("Gasto contable")),
    )

    INPUT, OUTPUT = "+", "-"
    INVENTORY_CHOICES = (
        (INPUT, _l("Entrada")),
        (OUTPUT, _l("Salida")),
    )

    CREDIT, DEBIT = "+", "-"
    ACCOUNT_CHOICES = (
        (CREDIT, _l("Crédito")),
        (DEBIT, _l("Débito")),
    )

    # Los tipos de este listado están habilitados para aceptar pagos.
    TYPES_THAT_CAN_ACCEPT_PAYMENTS = (INVOICE, INVOICE_RETURN, PURCHASE, 
        ACCOUNTING_INCOME, ACCOUNTING_EXPENSE)

    # Los tipos de este listado pueden afectar el inventario como entrada.
    TYPES_THAT_AFFECT_THE_INVENTORY_AS_INPUT = (INVENTORY_INPUT, PURCHASE,
        INVOICE_RETURN)

    # Los tipos de este listado pueden afectar el inventario como salida.
    TYPES_THAT_AFFECT_THE_INVENTORY_AS_OUTPUT = (INVENTORY_OUTPUT, INVOICE)

    # Los tipos de este listado pueden afectar el costo de artículos.
    TYPES_THAT_CAN_AFFECT_THE_COST = (INVOICE, INVOICE_RETURN, PURCHASE, 
        INVENTORY_INPUT, INVENTORY_OUTPUT)

    # Los tipos de este listado pueden afectar la cuenta por cobrar.
    TYPES_THAT_CAN_AFFECT_THE_ACCOUNT_RECEIVABLE = (INVOICE, ACCOUNTING_INCOME)

    # Los tipos de este listado pueden afectar la cuenta por pagar.
    TYPES_THAT_CAN_AFFECT_THE_ACCOUNT_PAYABLE = (PURCHASE, INVOICE_RETURN,
        ACCOUNTING_EXPENSE)

    code = models.CharField(_l("código"), max_length=6)

    name = models.CharField(_l("nombre"), max_length=70)

    generic_type = models.CharField(_l("tipo genérico"), max_length=20, 
    choices=GENERIC_TYPE_CHOICES, 
    help_text=_l("tipo genérico al que pertenece."))

    # affect_inventory = models.BooleanField(_l("afecta el inventario"), 
    # default=False, help_text=_l("Determina si los movimientos que se realicen "
    # "con este tipo de documento van a afectar el inventario de artículos."))

    affect_cost = models.BooleanField(_l("afecta el costo"), default=False, 
    help_text=_l("indica si el costo promedio de los artículos será calculado."))

    # affect_accounting_account = models.BooleanField(
    # _l("afecta las cuentas contable"), default=True, )

    tax_receipt = models.ForeignKey("finance.TaxReceipt", blank=True, null=True,
    on_delete=models.PROTECT, verbose_name=_l("comprobante fiscal"))

    is_active = models.BooleanField(_l("activo"), default=True)

    objects = models.Manager()

    active_objects = DocumentTypeActiveManager()

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
        
        other = DocumentType.objects.filter(
            company=self.company, code=self.code).exclude(pk=self.pk)
        if other:
            raise ValidationError({"code", 
                _("Ya existe otro tipo de documento con este código.")})

    def save(self, *args, **kwargs):
        self.code = " ".join(self.code.split()).upper()
        return super().save(*args, **kwargs)

    def accept_payments(self):
        """Determina si este tipo de documentos acepta pagos."""
        if self.generic_type in self.TYPES_THAT_CAN_ACCEPT_PAYMENTS:
            return True
        return False


class InputDocumentManager(models.Manager):
    """Manejador solo para documentos que afectan el inventario como entrada."""
    def get_queryset(self):
        return super().get_queryset().filter(
            doctype__inventory=DocumentType.INPUT)


class OutputDocumentManager(models.Manager):
    """Manejador solo para documentos que afectan el inventario como salida."""
    def get_queryset(self):
        return super().get_queryset().filter(
            doctype__inventory=DocumentType.OUTPUT)


class TransferDocumentManager(models.Manager):
    """Manejador para documentos de tipo transferencia."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(doctype__generic_type=DocumentType.TRANSFER)


class Document(utils.ModelBase):
    """
    Documento.
    """

    company = None # La empresa será doctype.company

    warehouse = models.ForeignKey("warehouse.Warehouse", 
    on_delete=models.CASCADE, help_text=_l("almacén del documento."))

    transfer_warehouse = models.ForeignKey("warehouse.Warehouse", blank=True,
    null=True, default=None, on_delete=models.CASCADE, 
    related_name="document_transfer_set", help_text=_l("almacén a transferir."))

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

    # Documentos que afectan el inventario como entrada.
    input_document_objects = InputDocumentManager()

    # Documentos que afectan el inventario como salida.
    output_document_objects = OutputDocumentManager()

    # Documentos de tipo transferencia.
    transfer_objects = TransferDocumentManager()

    class Meta:
        verbose_name = _l("documento")
        verbose_name_plural = _l("documentos")
        constraints = [
            models.UniqueConstraint(fields=("doctype", "number"), 
                name="unique_doctype_number")
        ]

    def __str__(self):
        return self.get_number()
    
    def get_next_number_for_type(self, doctype=None):
        """Obtiene el siguiente número para el tipo de documento indicado."""
        try:
            mx = Document.objects.filter(doctype=doctype).order_by("number")[0]
        except (IndexError):
            return 1

        return mx.number + 1

    def get_absolute_url(self):
        path = f"document-document-{self.doctype.generic_type}-update"
        return reverse_lazy(path, 
            kwargs={"company": self.doctype.company.pk, "pk": self.pk})

    def clean(self):
        if not self.pk:
            self.number = self.get_next_number_for_type(self.doctype)

        self.validate_transfer_warehouse()

    def validate_transfer_warehouse(self):
        """Valida que el campo 'transfer_warehouse'."""
        # La transferencia entre almacenes es exclusiva para los 
        # documentos de tipo transferencia.
        if self.doctype.generic_type == DocumentType.TRANSFER:
            if not self.transfer_warehouse:
                raise ValidationError(_("Debe indicar el almacén a transferir."))
        elif self.transfer_warehouse:
            raise ValidationError(_("Las transferencias entre almacenes son "
                "exclusivas de los documentos de tipo transferencia."))
        # El campo warehouse debe ser distinto a transfer_warehouse.
        if self.warehouse == self.transfer_warehouse:
            raise ValidationError({"warehouse": _("El almacén a transferir "
                "debe ser distinto al almacén del documento.")})
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.number = self.get_next_number_for_type(self.doctype)
        
        if self.currency_rate == None:
            self.currency_rate = self.currency.rate or 1

        self.validate_transfer_warehouse()
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

    def get_number(self, doctype=None, number=None):
        """Contruye y obtiene el número vísible del documento con su tipo."""
        doctype = doctype or getattr(self, "doctype", None)
        number = number or getattr(self, "number", "")

        if doctype and number:
            return "{}-{:0>12}".format(doctype, number)
        elif doctype:
            return "{}-{:0>12}".format(doctype, 
                self.get_next_number_for_type(doctype))
        else:
            return "{:0>12}".format(number)

    def get_person_name(self):
        return str(self.person or self.person_name)

    def get_balance(self):
        """Obtiene el saldo de este documento."""
        self.calculate() # Actualizamos primero por si acaso.
        credit_sum = self.get_credits().aggregate(s=Sum("amount"))["s"] or 0
        debit_sum = self.get_debits().aggregate(s=Sum("amount"))["s"] or 0
        trans_sum = credit_sum - debit_sum
        return self.total - trans_sum

    def get_credits(self):
        """
        Obtiene las transacciones de tipo crédito relativos a este documento.
        Relativo al documento porque no se considera si la transacción a sido 
        un crédito/débito para la empresa, sino que se considera si ha sido un 
        credito/debito para el documento dependiendo su tipo.
        """
        return self.get_transactions().filter(mode=Transaction.CREDIT)

    def get_debits(self):
        """Igual que get_relative_credits pero con los débitos."""
        return self.get_transactions().filter(mode=Transaction.DEBIT)

    def get_transactions(self):
        """Obtiene las transacciones contables realizadas a este documento."""
        return self.transaction_set.all()


