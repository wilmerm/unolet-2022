
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l





class Module(models.Model):
    """
    Un módulo es una parte del sistema encarcada de la gestión de determinadas
    funciones. Por lo general será un módulo para cada aplicación.

    Los módulos pueden ser hijos de otros módulos, para poder crear así el 
    efecto de lista desplegable.

    """

    name = models.CharField(_l("nombre"), max_length=70)

    description = models.CharField(_l("descripción"), max_length=200, blank=True)


    class Meta:
        verbose_name = _l("módulo")
        verbose_name_plural = _l("módulos")

    
    def __str__(self):
        return self.name