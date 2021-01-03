from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l


class Currency(models.Model):
    """
    Moneda.

    La moneda principal será la primera que se registre, y no podrá cambiarse 
    por otra. Se pueden realizar ajustes de cambio de simbolo, etc. pero la 
    tasa no podrá variar siempre será igual a 1. Esto es para evitar problemas
    de conversión en transacciones y documentos realizados.
    """

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    code = models.CharField(_l("código"), max_length=3, 
    help_text=_l("código ISO."))

    symbol = models.CharField(_l("símbolo"), max_length=10, 
    help_text=_l("símbolo de dinero."))

    name = models.CharField(_l("nombre"), max_length=50)

    rate = models.DecimalField(_l("tasa"), max_digits=10, decimal_places=2, 
    default=1)

    is_default = models.BooleanField(_("moneda predeterminada"), default=False,
    editable=False)

    class Meta:
        verbose_name = _l("moneda")
        verbose_name_plural = _l("monedas")
        ordering = ["is_default", "code"]
        constraints = [
            models.UniqueConstraint(fields=("company", "code"), 
                name="unique_company_currency"),
        ]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        # Solo habrá una moneda principal y esta 
        # será la primera que se registre.
        if not self.get_default():
            self.is_default = True
            self.rate = 1
        else:
            self.is_default = False

        return super().save(*args, **kwargs)

    def get_default(self):
        """Obtiene la moneda predeterminada del sistema para la empresa."""
        qs = Currency.objects.filter(is_default=True, company=self.company)
        return qs.last()
        