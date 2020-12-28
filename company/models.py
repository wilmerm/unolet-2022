from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from unoletutils.libs import utils



class Company(models.Model, utils.ModelBase):
    """
    Representa una empresa en la base de datos.

    Una empresa es una entidad que pertenece a un site y puede contener varios
    almacenes. Entonces las empresas tendrían el 2do nivel de prioridad después
    de los sites.
    """

    site = models.ForeignKey(Site, on_delete=models.PROTECT, editable=False)

    name = models.CharField(_l("nombre"), max_length=100,
    help_text=_l("nombre de la empresa para el público."))

    business_name = models.CharField(_l("Razón social"), max_length=100,
    help_text=_l("nombre legal registrado de la empresa."))

    is_active = models.BooleanField(_l("activo"), default=True)

    objects = models.Manager()

    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _l("empresa")
        verbose_name_plural = _l("empresas")
        ordering = ["site", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        if not self.pk:
            self.site = Site.objects.get_current()