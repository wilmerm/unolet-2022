from django.db import models
from django.db.models import Sum, Avg, F
from django.core.exceptions import ValidationError
from django.core.validators import (MinValueValidator, MaxValueValidator)
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse_lazy

from unoletutils.libs import utils, icons
from unoletutils.models import ModelBase


def get_default_currency():
    """Obtiene la moneda marcada como predeterminada."""
    from finance.models import Currency
    return Currency.objects.filter(is_default=True).last()


class ItemGroup(ModelBase):
    """
    Grupo de artículos.
    """
    name = models.CharField(_l("grupo"), max_length=50)

    class Meta:
        verbose_name = _l("grupo")
        verbose_name_plural = _l("grupos")
        constraints = [
            models.UniqueConstraint(fields=("company", "name"), 
                name="unique_company_group")
        ]

    def __str__(self):
        return self.name

    def clean(self):
        self.name = " ".join(self.name.split()).upper()

    def save(self, *args, **kwargs):
        self.name = " ".join(self.name.split()).upper()
        return super().save(*args, **kwargs)


class ItemFamily(ModelBase):
    """
    Familia de artículos.
    """
    name = models.CharField(_l("familia"), max_length=50)

    class Meta:
        verbose_name = _l("familia")
        verbose_name_plural = _l("familias")
        constraints = [
            models.UniqueConstraint(fields=("company", "name"), 
                name="unique_company_family")
        ]

    def __str__(self):
        return self.name

    def clean(self):
        self.name = " ".join(self.name.split()).upper()

    def save(self, *args, **kwargs):
        self.name = " ".join(self.name.split()).upper()
        return super().save(*args, **kwargs)


class ItemActiveManager(models.Manager):
    """Obtiene solo los items activos."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    

class Item(ModelBase):
    """
    Artículo de inventario.
    """
    ICON = "/static/img/box.svg"

    # Código único del artículo para cada empresa.
    code = models.CharField(_l("código"), max_length=8, editable=False)
    
    codename = models.CharField(_l("referencia"), max_length=30, 
    help_text=_l("Puede ser el módelo, serie, identificador, etc. Esta "
    "referencia debería ser única pero puede tener artículos con la misma "
    "referencia si así lo desea. Unolet le advertirá antes de crear un "
    "artículo con una referencia que ya existe para evitar duplicados no "
    "deseados."))

    name = models.CharField(_l("nombre"), max_length=70)

    description = models.CharField(_l("descripción"), max_length=500, 
    blank=True)

    group = models.ForeignKey(ItemGroup, on_delete=models.SET_NULL, null=True, 
    blank=True, verbose_name=_l("grupo"),
    help_text=_l("grupo de artículos al que pertenece."))

    family = models.ForeignKey(ItemFamily, on_delete=models.SET_NULL, null=True, 
    blank=True, verbose_name=_l("familia"),
    help_text=_l("Puede ser la marca del fabricante."))

    tax = models.ForeignKey("finance.Tax", on_delete=models.SET_NULL,
    blank=True, null=True)

    min_price = models.DecimalField(_l("precio mínimo"), max_digits=22, 
    decimal_places=2, default=0, blank=True)

    max_price = models.DecimalField(_l("precio máximo"), max_digits=22,
    decimal_places=2, default=0, blank=True)

    available = models.DecimalField(_l("disponible"), max_digits=22, 
    decimal_places=2, default=0, blank=True, editable=False)

    is_active = models.BooleanField(_l("activo"), default=True)

    is_service = models.BooleanField(_l("es un artículo de servicio"), 
    default=False)

    objects = models.Manager()

    active_objects = ItemActiveManager()

    class Meta:
        verbose_name = _l("artículo")
        verbose_name_plural = _l("artículos")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=["company", "code"], 
                name="unique_company_item")
        ]

    def __str__(self):
        return self.codename

    def get_absolute_url(self):
        return reverse_lazy("inventory-item-update", 
            kwargs={"company": self.company.pk, "pk": self.pk})

    @classmethod
    def get_next_code(cls, company) -> str:
        """Obtiene el siguiente código disponible para la compañia indicada."""
        return str(Item.objects.filter(company=company).count() + 1)
    
    def clean(self):
        self.codename = " ".join(self.codename.split()).upper()

        # Sus related fields deben pertenecer a la misma empresa.
        if self.group:
            if self.group.company != self.company:
                self.group = None
    
        if self.family:
            if self.family.company != self.company:
                self.family = None

    def update_tags(self):
        """Actualiza el valor del campo 'tags'."""
        self.tags = self.get_tags(self.code, self.codename, self.name, 
            self.group or "", self.family or "", combinate=True)
        self.tags += self.get_tag(self.description, combinate=True)
        self.tags = self.tags[:700]
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = self.get_next_code(self.company)
        self.codename = " ".join(self.codename.split()).upper()
        self.update_tags()
        return super().save(*args, **kwargs)

    def get_available(self, warehouse=None):
        """Obtiene la cantidad disponible global de este artículo."""
        if self.is_service:
            return 0

        from document.models import Document
        
        inputs = Movement.input_objects.filter(item=self)
        outputs = Movement.output_objects.filter(item=self)
        trans = Movement.transfer_objects.filter(item=self)

        if warehouse != None:
            inputs = inputs.filter(document__warehouse=warehouse)
            inputs = inputs | trans.filter(document__transfer_warehouse=warehouse)
            outputs = outputs.filter(document__warehouse=warehouse)
            outputs = outputs | trans.filter(document__warehouse=warehouse)

        input_sum = inputs.aggregate(s=models.Sum("quantity"))["s"] or 0
        output_sum = outputs.aggregate(s=models.Sum("quantity"))["s"] or 0
        return input_sum - output_sum

    def get_average_cost(self):
        """Obtiene el costo promedio de este artículo."""
        from document.models import DocumentType
        generic_types = DocumentType.TYPES_THAT_CAN_AFFECT_THE_COST
        qs = self.movement_set.filter(document__doctype__generic__in=generic_types)
        return qs.aggregate(a=Avg("total"))["a"] or 0


class InputMovementManager(models.Manager):
    """Manager para movimientos que afectan el inventario como entrada."""

    def get_queryset(self):
        from document.models import DocumentType
        generic_types = DocumentType.TYPES_THAT_AFFECT_THE_INVENTORY_AS_INPUT
        return super().get_queryset().filter(
            document__doctype__generic__in=generic_types)
        formula = ((F("price") * F("quantity")) - F("discount")) + F("tax")
        qs = qs.annotate(total=formula)
        return qs


class OutputMovementManager(models.Manager):
    """Manager para movimientos que afectan el inventario como salida."""

    def get_queryset(self):
        from document.models import DocumentType
        generic_types = DocumentType.TYPES_THAT_AFFECT_THE_INVENTORY_AS_OUTPUT
        return super().get_queryset().filter(
            document__doctype__generic__in=generic_types)
        formula = ((F("price") * F("quantity")) - F("discount")) + F("tax")
        qs = qs.annotate(total=formula)
        return qs


class TransferMovementManager(models.Manager):
    """Manager para movimientos que pertenecen a transferencia de inventario."""

    def get_queryset(self):
        from document.models import DocumentType
        qs = super().get_queryset().filter(
            document__doctype__generic=DocumentType.TRANSFER)
        return qs


class MovementManager(models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        formula = ((F("price") * F("quantity")) - F("discount")) + F("tax")
        qs = qs.annotate(total=formula)
        return qs


class Movement(ModelBase):
    """
    Movimiento de inventario.
    """

    # No elegimos 'item__company' porque el item puede ser nulo.
    COMPANY_FIELD_NAME = "document__doctype__company"

    company = None # la empresa será document.doctype.company

    document = models.ForeignKey("document.Document", on_delete=models.CASCADE)

    number = models.IntegerField(_l("número"), default=1, editable=False)

    # El artículo puede ser nulo, así existe la posibilidad de que se puedan 
    # registrar movimientos contables, commo ingresos o gastos, o simplemente
    # artículos de servicios que no estén registrados como tal.
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, 
    null=True, verbose_name=_l("artículo"))

    name = models.CharField(_l("nombre"), max_length=70, blank=True)

    quantity = models.DecimalField(_l("cantidad"), max_digits=12, 
    decimal_places=2, validators=[MinValueValidator(0)])

    price = models.DecimalField(_l("precio"), max_digits=22, decimal_places=2,
    validators=[MinValueValidator(0)])

    discount = models.DecimalField(_l("descuento"), max_digits=22, 
    decimal_places=2, validators=[MinValueValidator(0)])

    tax = models.DecimalField(_l("impuesto"), max_digits=22, decimal_places=2,
    blank=True, default=0, editable=False, validators=[MinValueValidator(0)])

    tax_already_included = models.BooleanField(_l("impuesto ya incluido"), 
    default=False, help_text=_l("Indica que el impuesto ya está incluido en el "
    "monto (precio) especificado, entonces se extraerá el impuesto del monto "
    "indicado (si aplica)."))

    objects = MovementManager()

    # Manejador para movimientos en documentos que afectan el inv. como entrada.
    input_objects = InputMovementManager()

    # Manejador para movimientos en documentos que afectan el inv. como salida.
    output_objects = OutputMovementManager()

    # Manejador para movimientos en documentos de tipo transferencia.
    transfer_objects = TransferMovementManager()

    class Meta:
        verbose_name = _l("movimiento")
        verbose_name_plural = _l("movimientos")
        ordering = ["number"]

    def __str__(self):
        return f"{self.item} = {self.quantity}"

    def _get_next_number(self):
        try:
            return Movement.objects.filter(
                document=self.document).order_by("-number")[0].number + 1
        except (IndexError):
            return 1

    def save(self, *args, **kwargs):
        """
        Guarda el movimiento. 

        Hay un parámetro opcional:
            not_calculate_document (bool): Determina si se calculará o no los 
            campos en el documento para actualizar sus campos con 
            document.calculate()
        """
        if not self.name:
            self.name = self.item.name 

        # Establecemos el impuesto a self.tax
        self.calculate_tax()

        # Este parámetro determinará si se ejecutará self.document.calculate()
        # Es útil cuando intentamos guardar muchos movimiento a la vez, ya que 
        # en el mismo método calculate del documento se recorrerán cada uno de
        # los movimientos.
        try:
            not_calculate_document = bool(kwargs.pop("not_calculate_document"))
        except (KeyError):
            not_calculate_document = False

        if not getattr(self, "number", None):
            self.number = self._get_next_number()

        # La empresa en el documento debe ser la misma empresa del artículo.
        # document.doctype.company == item.company
        if self.document.doctype.company != self.item.company:
            raise ValidationError(
                _("La empresa del documento y el artículo no es la misma."))
        
        out = super().save(*args, **kwargs)

        # Actualizamos los campos de consulta en el documento relacionado.
        if not not_calculate_document:
            self.document.calculate()

        return out

    def get_img(self):
        if self.document.is_inventory_input():
            return "/static/icons/cart-plus-fill.svg"
        elif self.document.is_inventory_output:
            return "/static/icons/cart-dash-fill.svg"
        return "/static/icons/cart3.svg"

    def get_icon(self):
        if self.document.is_inventory_input():
            return icons.svg("cart-plus-fill.svg", fill="var(--green)")
        elif self.document.is_inventory_output:
            return icons.svg("cart-dash-fill.svg", fill="var(--red)")
        return icons.svg("cart3.svg")

    def get_total_formula(self):
        """expresión usada para calcular el total en un queryset con annotate"""
        return ((F("price") * F("quantity")) - F("discount")) + F("tax")

    def get_local_total_formula(self):
        """Igual que get_total_formula pero tomando en cuenta la divisa."""
        if self.document.currency_rate:
            return self.get_total_formula() * F("document__currency_rate")
        return self.get_total_formula()

    def calculate_tax(self):
        """Calcula el impuesto según el artículo y el documento."""
        if self.document.pay_taxes and self.item.tax:
            self.tax = self.item.tax.calculate(self.get_amount_with_discount())
        else:
            self.tax = 0

        return self.tax

    def get_amount(self):
        """Obtiene el importe (cantidad x precio)."""
        return (self.price * self.quantity)

    def get_amount_with_discount(self):
        """Obtiene el importe ((cantidad * precio) - descuento)."""
        return (self.price * self.quantity) - self.discount

    def get_total(self):
        """Obtiene el total ((cantidad * precio) - descuento) + impuesto."""
        return self.get_amount_with_discount() + self.tax

    def get_local_amount(self):
        """Igual que self.get_amount * self.document.currency_rate."""
        return self.get_amount() * (self.document.currency_rate or 1)

    def get_local_amount_with_discount(self):
        """Igual self.get_amount_with_discount * self.document_currency_rate."""
        currency_rate = self.document.currency_rate or 1
        return self.get_amount_with_discount() * currency_rate

    def get_local_total(self):
        """Igual que self.get_total * self.document.currency_rate."""
        return self.get_total() * (self.document.currency_rate or 1)

    def get_available(self, warehouse=None):
        """
        Obtiene el disponible del artículo en este movimiento para el 
        almacén indicado o el almacén del documento de este movimiento.
        """
        if self.item == None:
            return 0
        warehouse = warehouse or self.document.warehouse
        return self.item.get_available(warehouse=warehouse)


