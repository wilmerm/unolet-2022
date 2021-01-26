
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ValidationError

from colorfield.fields import ColorField

from unoletutils.libs import utils, icons
from unoletutils.models import ModelBase


class Module(ModelBase):
    """
    Este modelo lo que hace es almacenar un urlpath, entonces asignamos 
    distintos módulos a los usuarios, y si un usuario accede a un urlpath se 
    verifica que sea parte de un módulo con dicho urlpath, de no ser así se 
    prohibirá su acceso en la vista.

    Un módulo es una parte del sistema encarcada de la gestión de determinadas
    funciones. Por lo general será un módulo para cada aplicación.

    Los módulos pueden ser hijos de otros módulos, para poder crear así el 
    efecto de lista desplegable.
    """

    ADMIN = "admin"
    INVENTORY = "inventory"

    BASE_MODULE_CHOICES = (
        (ADMIN, _l("Administración")),
        (INVENTORY, _l("Inventario")),
    )

    ICON_CHOICES = [(i, i) for i in icons.DATA.keys()]
    ICON_CHOICES.sort()
    ICON_CHOICES = tuple(ICON_CHOICES)

    company = None

    name = models.CharField(_l("nombre"), max_length=70, unique=True)

    description = models.CharField(_l("descripción"), max_length=200, blank=True)

    url_name = models.CharField(unique=True, max_length=256)

    icon_name = models.CharField(_l("ícono"), max_length=100, blank=True,
    choices=ICON_CHOICES)

    parent = models.ForeignKey("module.Module", on_delete=models.CASCADE, 
    blank=True, null=True, help_text=_l("módulo padre al cual pertenece."))

    css_bgcolor = ColorField(_l("Color del fondo"), default="#404040")

    css_textcolor = ColorField(_l("Color del texto"), default="#FFFFFF")

    class Meta:
        verbose_name = _l("módulo")
        verbose_name_plural = _l("módulos")
        ordering = ["url_name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self, company):
        company = int(getattr(company, "pk", company))
        return reverse_lazy(self.url_name, kwargs={"company": company})
    
    def clean(self):
        # No puede ser hijo de si mismo.
        if self.parent == self:
            raise ValidationError({"parent": _("No puede ser hijo de si mismo.")})

    def get_icon(self):
        return icons.get_url(self.icon_name)

    def get_svg(self, size: str=None, fill: str=None):
        return icons.svg(self.icon_name, size=size, fill=fill, id=f"module_{self.id}")

    @staticmethod
    def get_from_request(request):
        """Obtiene el modulo a partir del request.resolver_match.url_name."""
        try:
            return Module.objects.get(url_name=request.resolver_match.url_name)
        except (Module.DoesNotExist):
            return None
        
    def build_url(self, **kwargs):
        """
        Construye la url para el self.url_name con reverse. Los parámetros 
        pasados se pasarán igual a la función reverse de Django.
        """
        return reverse(self.url_name, kwargs=kwargs)
