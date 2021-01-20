from decimal import Decimal

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

    # INPUT, OUTPUT = "+", "-"
    # INVENTORY_CHOICES = (
    #     (INPUT, _l("Entrada")),
    #     (OUTPUT, _l("Salida")),
    # )

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

    sequence = models.IntegerField(_l("secuencia"), editable=False, null=True)

    number = models.CharField(_l("número"), max_length=30, blank=True)

    person = models.ForeignKey("person.Person", on_delete=models.PROTECT, 
    null=True, blank=True, verbose_name=_l("persona"))

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

    pay_taxes = models.BooleanField(_l("Paga impuestos"), default=True, 
    help_text=_l("Determina si este documento paga impuestos."))

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

    # Manejadores.

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
            models.UniqueConstraint(fields=("doctype", "sequence"), 
                name="unique_document_doctype_sequence")
        ]

    def __str__(self):
        return self.get_number()

    def get_reverse_kwargs(self):
        """Obtiene el diccionario para construir la URL con reverse."""
        print("hola")
        return {
            "company": self.doctype.company.pk,
            "generictype": self.doctype.generic_type, "pk": self.pk}

    def get_absolute_url(self, mode="update"):
        return reverse_lazy(f"document-document-{mode}", 
            kwargs=self.get_reverse_kwargs())

    def get_detail_url(self):
        return self.get_absolute_url("detail")

    def get_update_url(self):
        return self.get_absolute_url("update")
    
    def get_delete_url(self):
        return self.get_absolute_url("delete")

    def get_create_url(self):
        kwargs = self.get_reverse_kwargs()
        kwargs.pop("pk")
        return reverse_lazy("document-document-create", kwargs=kwargs)

    def get_list_url(self):
        kwargs = self.get_reverse_kwargs()
        kwargs.pop("pk")
        return reverse_lazy("document-document-list", kwargs=kwargs)

    def clean(self):
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
            self.sequence = self.get_next_sequence_for_type(self.doctype)
            if not self.number:
                self.number = "{:0>12}".format(self.sequence)

            if not self.person_name:
                self.person_name = str(self.person)
        
        if self.currency_rate == None:
            self.currency_rate = self.currency.rate or 1

        self.validate_transfer_warehouse()
        return super().save(*args, **kwargs)

    def calculate(self) -> dict:
        """
        Calcula los totales, actualiza los campos correspondientes y retorna 
        un diccionario con los resultados.
        """
        qs = self.movement_set.all()
        out = {"amount": 0, "discount": 0, "tax": 0, "total": 0, 
            "movements": qs, "updated": False}

        if qs:
            out["amount"] = qs.aggregate(s=Sum(F("quantity") * F("price")))["s"]
            out["discount"] = qs.aggregate(s=Sum("discount"))["s"]
            out["tax"] = qs.aggregate(s=Sum("tax"))["s"]
            out["total"] = qs.aggregate(s=Sum(
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
    
    def get_number(self, doctype=None, sequence=None) -> str:
        """Contruye y obtiene el número visible del documento con su tipo."""
        doctype = doctype or getattr(self, "doctype", None)
        sequence = sequence or getattr(self, "sequence", "")

        if doctype and sequence:
            return "{}-{:0>12}".format(doctype, sequence)
        elif doctype:
            return "{}-{:0>12}".format(doctype, 
                self.get_next_sequence_for_type(doctype))
        else:
            return "{:0>12}".format(sequence)

    @classmethod
    def get_next_sequence_for_type(cls, doctype=None):
        """Obtiene la siguiente secuencia para el tipo de documento indicado."""
        try:
            mx = Document.objects.filter(
                doctype=doctype).order_by("-sequence")[0]
        except (IndexError):
            return 1
        
        if mx.sequence == None:
            mx.sequence = 1
            mx.number = "{:0>12}".format(1)
            mx.save()
        return mx.sequence + 1

    def get_person_name(self):
        return str(self.person or self.person_name)

    def get_movements(self) -> models.QuerySet:
        """Obtiene los movimientos de este documento."""
        return self.movement_set.all()

    def get_balance(self) -> Decimal:
        """Obtiene el saldo de este documento."""
        self.calculate() # Actualizamos primero por si acaso.
        credit_sum = self.get_credits().aggregate(s=Sum("amount"))["s"] or 0
        debit_sum = self.get_debits().aggregate(s=Sum("amount"))["s"] or 0
        total_sum = credit_sum - debit_sum
        return self.total - total_sum

    def get_credits(self) -> models.QuerySet:
        """
        Obtiene las transacciones de tipo crédito relativos a este documento.
        Relativo al documento porque no se considera si la transacción a sido 
        un crédito/débito para la empresa, sino que se considera si ha sido un 
        credito/debito para el documento dependiendo su tipo.
        """
        return self.get_transactions().filter(mode=Transaction.CREDIT)

    def get_debits(self) -> models.QuerySet:
        """Igual que get_relative_credits pero con los débitos."""
        return self.get_transactions().filter(mode=Transaction.DEBIT)

    def get_transactions(self) -> models.QuerySet:
        """Obtiene las transacciones contables realizadas a este documento."""
        return self.transaction_set.all()


class DocumentNote(utils.ModelBase):
    """
    Notas que se agregarán a los documentos como comentarios de los usuarios.
    
    En estas notas podrán especificar, por ejemplo, por qué se modifica el 
    documento, etc.
    """ 
    company = None # La empresa será la misma del documento al que pertenece.
    tags = None

    document = models.ForeignKey(Document, on_delete=models.CASCADE, 
    verbose_name=_l("documento"))

    create_user = models.ForeignKey("user.User", on_delete=models.SET_NULL, 
    null=True)

    create_date = models.DateTimeField(_l("fecha"), auto_now_add=True)

    # El usuario podrá ser eliminado, y la relación romperse, pero esta nota 
    # seguirá existiendo con el nombre de usuario puesto en este campo.
    username = models.CharField(_l("nombre de usuario"), max_length=100, 
    blank=True, editable=False)

    content = models.CharField(_l("contenido"), max_length=200)

    class Meta:
        verbose_name = _l("nota")
        verbose_name_plural = _l("notas")
        ordering = ["-create_date"]

    def __str__(self):
        if len(self.content) > 30:
            return "{}...".format(self.content[:30])
        return self.content

    def clean(self):
        self.content = self.strip(self.content)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = str(self.create_user)
        return super().save(*args, **kwargs)