from django.db import models

from unoletutils.models import ModelBase



class PrintTemplate(ModelBase):
    """
    Plantilla de impresión.
    """
    tags = None

    name = models.CharField(_l("nombre"), max_length=100)

    content = models.TextField(_l("contenido"), help_text=_l("contenido de la "
    "plantilla en formato HTML."))

    class Meta:
        verbose_name = _l("plantilla de impresión")
        verbose_name_plural = _l("plantillas de impresión")
    
    def __str__(self):
        return self.name

    


    

