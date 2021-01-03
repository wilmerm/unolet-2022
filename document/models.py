from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse_lazy


class DocumentType(models.Model):
    """
    Tipo de documento.
    """
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    code = models.CharField(_l("código"), max_length=6)

    name = models.CharField(_l("nombre"), max_length=70)

    class Meta:
        verbose_name = _l("tipo de documento")
        verbose_name_plural = _l("tipos de documentos")
        constraints = [
            models.UniqueConstraint(fields=("company", "code"), 
                name="unique_company_documenttype")
        ]

    def __str__(self):
        return self.code
    
    def clean(self):
        self.code = " ".join(self.code.split()).upper()
        
        if DocumentType.objects.filter(company=self.company).exclude(pk=self.pk):
            raise ValidationError({"code", 
                _("Ya existe otro tipo de documento con este código.")})

    def save(self, *args, **kwargs):
        self.code = " ".join(self.code.split()).upper()
        return super().save(*args, **kwargs)


class Document(models.Model):
    """
    Documento.
    """

    doctype = models.ForeignKey(DocumentType, on_delete=models.PROTECT,
    verbose_name=_l("tipo"))

    number = models.IntegerField(_l("número"), editable=False)

    person = models.ForeignKey("person.Person", on_delete=models.PROTECT, 
    null=True, blank=True)

    person_name = models.CharField(_l("nombre de la persona"), max_length=100,
    blank=True)

    note = models.CharField(_l("nota"), max_length=500, blank=True)

    # Campos para consultas.

    amount = models.DecimalField(_l("importe"), max_digits=32, decimal_places=2,
    null=True, blank=True)

    discount = models.DecimalField(_l("descuento"), max_digits=32, 
    decimal_places=2, null=True, blank=True)

    tax = models.DecimalField(_l("impuesto"), max_digits=32, 
    decimal_places=2, null=True, blank=True)

    total = models.DecimalField(_l("total"), max_digits=32, 
    decimal_places=2, null=True, blank=True)

    # Seguimiento.

    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, 
    on_delete=models.PROTECT, null=True, blank=True)

    create_date = models.DateTimeField(_l("fecha de creación"), 
    auto_now_add=True)

    class Meta:
        verbose_name = _l("documento")
        verbose_name_plural = _l("documentos")
        constraints = [
            models.UniqueConstraint(fields=("doctype", "number"), 
                name="unique_doctype_number")
        ]

    def __str__(self):
        return "{}-{:0>12}".format(self.doctype, self.number)
    
    @classmethod
    def _get_next_number_for_type(cls, doctype=None):
        """Obtiene el siguiente número para el tipo de documento indicado."""
        try:
            mx = Document.objects.filter(doctype=doctype).order_by("number")[0]
        except (IndexError):
            return 1

        return mx.number + 1

    def get_absolute_url(self):
        return reverse_lazy("document-document-update", 
            kwargs={"company": self.doctype.company.pk, "pk": self.pk})

    def clean(self):
        if not self.pk:
            self.number = self._get_next_number_for_type(self.doctype)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.number = self._get_next_number_for_type(self.doctype)
        return super().save(*args, **kwargs)
