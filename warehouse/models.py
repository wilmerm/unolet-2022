from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse_lazy

from unoletutils.libs import utils
from company.models import Company


class WarehouseOnSiteManager(models.Manager):
    """Obtiene los almacenes que pertenecen a empresas del site actual."""

    def get_queryset(self):
        return super().get_queryset().filter(
            company__site=Site.objects.get_current())


class Warehouse(models.Model, utils.ModelBase):
    """
    Un almacén es una entidad del mundo real que pertenece a una empresa.

    Una empresa puede contener varios almacenes, pero un solo almacén 
    pertenecerá a una única empresa.

    Un almacén es un espacio donde se almacenan los artículos de inventario, se 
    realizan las operaciones presenciales de la empresa, etc. Un almacén bien 
    podría ser una sucursal de la empresa, una oficina, etc.

    Los documentos de que se realicen tendrán un almacén específico donde serán 
    creados. De modo que, dichos documentos, tendrán la información que se haya 
    configurado en dicho almacén.
    """

    company = models.ForeignKey(Company, on_delete=models.PROTECT, 
    help_text=_l("empresa a la que pertenece este almacén."))

    name = models.CharField(_l("nombre"), max_length=100,
    help_text=_l("nombre para el público."))

    address = models.CharField(_l("dirección"), max_length=500, blank=True)

    phones = models.CharField(_l("teléfonos"), max_length=100, blank=True)

    email = models.EmailField(_l("correo electrónico"), blank=True)

    is_active = models.BooleanField(_l("activo"), default=True)

    objects = models.Manager()

    on_site = WarehouseOnSiteManager()

    class Meta:
        verbose_name = _l("almacén")
        verbose_name_plural = _l("almacenes")
        ordering = ["company", "is_active", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy("warehouse-warehouse-detail", kwargs={"company": self.company.pk, "warehouse": self.pk})