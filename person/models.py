from django.db import models
from django.db.models import Sum, F
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from unoletutils.libs import utils
from unoletutils.models import ModelBase
from document.models import DocumentType, Document


class IdentificationType(ModelBase):
    """
    Tipo de identificación para personas.
    """

    ALLOWED = "allowed"
    NOT_ALLOWED = "not_allowed"
    MODE_CHOICES = (
        (ALLOWED, _l("Permitir")),
        (NOT_ALLOWED, _l("Prohibir")),
    )

    name = models.CharField(_l("nombre"), max_length=50)

    characters = models.CharField(_l("caracteres permitidos"), 
    max_length=500, default="0123456789",
    help_text=_l("Indique los caracteres que desea permitir o prohibir."))

    mode = models.CharField(_l("modo"), max_length=20, blank=True,
    choices=MODE_CHOICES, default=ALLOWED)

    max_length = models.IntegerField(_l("Longitud máxima"), default=11,
    blank=True, null=True, validators=[MinValueValidator(0)],
    help_text=_l("Longitud máxima permitida."))

    min_length = models.IntegerField(_l("Longitud mínima"), default=11,
    blank=True, null=True, validators=[MinValueValidator(0)],
    help_text=_l("Longitud mínima permitida."))

    class Meta:
        verbose_name = _l("tipo de identificación")
        verbose_name_plural = _l("tipos de identificaciones")
        constraints = [
            models.UniqueConstraint(fields=["company", "name"], 
                name="unique_identificationtype_name")
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.get_update_url()

    def clean(self):
        self.clean_name()

    def clean_name(self):
        self.name = self.strip(self.name)
        other = IdentificationType.objects.filter(
            name__iexact=self.name).exclude(pk=self.pk)
        if other:
            raise ValidationError(
            {"name": _("Ya existe un tipo de identificación con este nombre.")})
        return self.name

    def save(self, *args, **kwargs):
        self.clean_name()
        return super().save(*args, **kwargs)

    def validate_identification(self, text):
        """
        Valida que el texto pasado esté acorde con el formato configurado en
        este tipo de identificación.
        """
        # Se validan los caracteres permitidos.
        not_allowed = []
        if self.mode == self.ALLOWED:
            for char in text:
                if not char in self.characters:
                    not_allowed.append(char)
        elif self.mode == self.NOT_ALLOWED:
            for char in text:
                if char in self.characters:
                    not_allowed.append(char)
        if not_allowed:  
            raise ValidationError(_("El texto contiene los siguientes "
                "caracteres no permitidos: ") + "".join(not_allowed))

        # Se valida la longitud del texto.
        if self.min_length:
            if len(text) < self.min_length:
                raise ValidationError(
                _l("La cantidad mínima de caracteres es ") + str(self.min_length))
        if self.max_length:
            if len(text) > self.max_length:
                raise ValidationError(
                _l("La cantidad máxima de caracteres es ") + str(self.max_length))

        return text


class PersonActiveManager(models.Manager):
    """Obtiene solo las personas activas."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Person(ModelBase):
    """
    Persona.
    """

    ICON = "/static/img/person.svg"

    # Identificación única para cada persona en una empresa.
    identification = models.CharField(_l("identificación"), max_length=50)

    identification_type = models.ForeignKey(IdentificationType, 
    on_delete=models.SET_NULL, blank=True, null=True, default=None,
    verbose_name=_l("Tipo de identificación"))

    name = models.CharField(_l("nombre"), max_length=100)

    business_name = models.CharField(_l("nombre comercial"), max_length=100,
    blank=True)

    email = models.EmailField(_l("correo electrónico"), blank=True)

    phone = models.CharField(_l("teléfono"), max_length=20, blank=True)

    contact_person = models.ForeignKey("person.Person", 
    on_delete=models.SET_NULL, null=True, blank=True, 
    verbose_name=_l("persona de contacto"))

    credit_limit = models.DecimalField(_l("límite de crédito"), 
    max_digits=22, decimal_places=2, blank=True, default=0, 
    validators=[MinValueValidator(0)],
    help_text=_l("Límite de crédito permitido para esta persona."))

    credit_limit_days = models.IntegerField(
    _l("tiempo límite de crédito en días"), blank=True, default=0,
    validators=[MinValueValidator(0)])

    is_supplier = models.BooleanField(_l("es suplidor"), default=False, 
    help_text=_l("puede indicar si esta persona también es un suplidor."))

    is_active = models.BooleanField(_l("activo"), default=True)

    objects = models.Manager()

    active_objects = PersonActiveManager()

    class Meta:
        verbose_name = _l("persona")
        verbose_name_plural = _l("personas")
        constraints = [
            models.UniqueConstraint(fields=["company", "identification"], 
                name="unique_person_identification")
        ]

    def __str__(self):
        return self.name 
    
    def clean(self):
        self.clean_identification_type()
        self.clean_identification()

    def clean_identification_type(self):
        if not self.identification_type:
            return

        # El tipo de identificación y esta persona tienen que pertenecer 
        # a la misma empresa.    
        if self.identification_type.company != self.company:
            raise ValidationError(_("La empresa a la que pertenece esta "
                "persona y la del tipo de identificación son distintas."))

    def clean_identification(self):
        if not self.identification_type:
            return self.identification
        # Validamos seǵun los parámetros del tipo de identificación.
        return self.identification_type.validate_identification(self.identification)

    def save(self, *args, **kwargs):
        self.clean_identification_type()
        return super().save(*args, **kwargs)

    def get_document_account_receivable_pending_payment(self) -> dict:
        """
        Obtiene los documentos que esta persona tiene pendientes de pago.

        returns:
            {'queryset': Queryset, 'totals': dict}

        """
        out = dict()
        types = DocumentType.TYPES_THAT_CAN_AFFECT_THE_ACCOUNT_RECEIVABLE
        qs = self.document_set.filter(doctype__generic__in=types)
        qs = qs.annotate(balance=F("total")-Sum("transaction__amount"))
        qs = qs.filter(balance__gt=0)
        out["queryset"] = qs
        out["totals"] = qs.aggregate(
            Sum("total"), 
            Sum("transaction__amount"),
            Sum("balance")
        )
        out["totals"]["count"] = qs.count()
        return out

    def get_document_account_payable_pending_payment(self):
        """
        Obtiene los documentos que la empresa le debe a esta persona.

        returns:
            {'queryset': Queryset, 'totals': dict}

        """
        out = dict()
        types = DocumentType.TYPES_THAT_CAN_AFFECT_THE_ACCOUNT_PAYABLE
        qs = self.document_set.filter(doctype__generic__in=types)
        qs = qs.annotate(balance=F("total")-Sum("transaction__amount"))
        out["queryset"] = qs.filter(balance__gt=0)
        out["totals"] = qs.aggregate(
            Sum("total"), 
            Sum("transaction__amount"),
            Sum("balance")
        )
        return out

    def get_balance_account_receivable(self):
        """
        Obtiene el balance de la cuenta por cobrar de esta persona.
        (El balance que esta persona le debe a la empresa).
        """
        types = DocumentType.TYPES_THAT_CAN_AFFECT_THE_ACCOUNT_RECEIVABLE
        # Solo documentos que afectan la cuenta por cobrar.
        qs = self.document_set.filter(doctype__generic__in=types)
        return qs.aggregate(s=Sum("total")-Sum("transaction__amount")).get("s", 0)

    def get_balance_account_payable(self):
        """
        Obtiene el balance de la cuenta por pagar de esta persona.
        (El balance que la empresa le debe a esta persona).
        """
        types = DocumentType.TYPES_THAT_CAN_AFFECT_THE_ACCOUNT_PAYABLE
        # Solo documentos que afectan la cuenta por cobrar.
        qs = self.document_set.filter(doctype__generic__in=types)
        return qs.aggregate(s=Sum("total")-Sum("transaction__amount")).get("s", 0)

    def get_balance(self):
        """
        Obtiene el balance global de esta persona, tomando en cuenta tanto la 
        cuenta por pagar como la cuenta por cobrar.

        Asi que si el cliente debe 500, pero la empresa le debe a él 200 
        (por ser suplidor por ejemplo), entonces el balance será -300.

        Si desea solo el balance por el monto adeudado a la empresa, debe 
        utilizar 'get_balance_account_receivable', y 
        'get_balance_account_payable' para el balance que le debe la empresa a 
        dicho cliente.
        """
        types = DocumentType.TYPES_THAT_CAN_ACCEPT_PAYMENTS
        # Solo documentos que aceptan pagos.
        qs = self.document_set.filter(doctype__generic__in=types)
        return qs.aggregate(s=Sum("total")-Sum("transaction__amount")).get("s", 0)