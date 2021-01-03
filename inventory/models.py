from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import (MinValueValidator, MaxValueValidator)
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse_lazy

from unoletutils.libs import utils


def get_default_currency():
    """Obtiene la moneda marcada como predeterminada."""
    from finance.models import Currency
    return Currency.objects.filter(is_default=True).last()


class ItemGroup(models.Model, utils.ModelBase):
    """
    Grupo de artículos.
    """

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    name = models.CharField(_l("grupo"), max_length=50)

    class Meta:
        verbose_name = _l("grupo")
        verbose_name_plural = _l("grupos")
        constraints = [
            models.UniqueConstraint(fields=("company", "name"), 
                name="unique_company_group")
        ]

    def __str__(self):
        self.name

    def clean(self):
        self.name = " ".join(self.name.split()).upper()

    def save(self, *args, **kwargs):
        self.name = " ".join(self.name.split()).upper()
        return super().save(*args, **kwargs)


class ItemFamily(models.Model, utils.ModelBase):
    """
    Familia de artículos.
    """

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    
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
    

class Item(models.Model, utils.ModelBase):
    """
    Artículo de inventario.
    """

    # Todo artículo pertenecerá a una única empresa.
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)

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
    blank=True, help_text=_l("grupo de artículos al que pertenece."))

    family = models.ForeignKey(ItemFamily, on_delete=models.SET_NULL, null=True, 
    blank=True, help_text=_l("familia de artículos al que pertenece. Puede ser "
    "la marca del fabricante."))

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
    def _get_next_code(cls, company):
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
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = self._get_next_code(self.company)
        self.codename = " ".join(self.codename.split()).upper()
        return super().save(*args, **kwargs)


class Movement(models.Model, utils.ModelBase):
    """
    Movimiento de inventario.
    """

    document = models.ForeignKey("document.Document", on_delete=models.CASCADE)

    number = models.IntegerField(_l("número"), default=1)

    item = models.ForeignKey(Item, on_delete=models.CASCADE, 
    verbose_name=_l("artículo"))

    quantity = models.DecimalField(_l("cantidad"), max_digits=12, 
    decimal_places=2, validators=[MinValueValidator(0)])

    price = models.DecimalField(_l("precio"), max_digits=22, decimal_places=2,
    validators=[MinValueValidator(0)])

    discount = models.DecimalField(_l("descuento"), max_digits=22, 
    decimal_places=2, validators=[MinValueValidator(0)])

    tax = models.DecimalField(_l("impuesto"), max_digits=22, decimal_places=2,
    validators=[MinValueValidator(0)])

    currency = models.ForeignKey("finance.Currency", on_delete=models.PROTECT,
    default=get_default_currency, null=True, verbose_name=_l("moneda"))

    currency_rate = models.DecimalField(_l("tasa de cambio"), max_digits=10, 
    decimal_places=2, default=1, validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = _l("movimiento")
        verbose_name_plural = _l("movimientos")
        ordering = ["number"]

    def __str__(self):
        return "%s %s" % (self._meta.verbose_name, self.item)

    def _get_next_number(self):
        try:
            return Movement.objects.filter(
                document=self.document).order_by("-number")[0].number + 1
        except (IndexError):
            return 1

    def save(self, *args, **kwargs):
        if not getattr(self, "number", None):
            self.number = self._get_next_number()
        super().save(*args, **kwargs)

    def get_amount(self):
        """Obtiene el importe ((cantidad x precio) - descuento)."""
        return (self.price * self.quantity) - self.discount

    def get_total(self):
        """Obtiene el total ((cantidad x precio) - descuento) + impuesto."""
        return self.get_amount() + self.tax

