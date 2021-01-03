
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l





class Module:
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


    name = models.CharField(_l("nombre"), max_length=70, unique=True)

    description = models.CharField(_l("descripción"), max_length=200, blank=True)

    urlpath = models.CharField(unique=True, max_length=100)

    icon = models.ImageField(upload_to="module/module/")


    class Meta:
        verbose_name = _l("módulo")
        verbose_name_plural = _l("módulos")
        ordering = ["urlpath"]

    def __str__(self):
        return self.name