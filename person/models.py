from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l



class Person(models.Model):
    """
    Persona.
    """

    # Identificación única para cada persona en una empresa.
    identification = models.CharField(_l("identificación"), max_length=50)
