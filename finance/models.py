from django.db import models, IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import (MinValueValidator, MaxValueValidator, 
    MinLengthValidator, MaxLengthValidator)
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from unoletutils.libs import utils


class Currency(utils.ModelBase):
    """
    Moneda.

    La moneda principal será la primera que se registre, y no podrá cambiarse 
    por otra. Se pueden realizar ajustes de cambio de simbolo, etc. pero la 
    tasa no podrá variar siempre será igual a 1. Esto es para evitar problemas
    de conversión en transacciones y documentos realizados.
    """
    
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


class TaxReceipt(utils.ModelBase):
    """
    Comprobante fiscal.
    """
    tags = None

    code = models.CharField(_l("código"), max_length=2,
    help_text=_l("código del tipo de comprobante según la DGII."))

    name = models.CharField(_l("nombre"), max_length=100,
    help_text=_l("nombre del tipo de comprobante físcal."))

    is_active = models.BooleanField(_l("activo"), default=True)

    min_available_to_notify = models.IntegerField(
    verbose_name=_l("disponible mínimo para avisar"), 
    validators=(MinValueValidator(0),), default=0,
    help_text=_l("notifica al usuario cuando el disponible alcance este valor."))

    min_days_before_expiration_to_notify = models.IntegerField(
    verbose_name=_l("días mínimos antes de vencer para avisar"), 
    validators=(MinValueValidator(0),),
    default=0, help_text=_l("notifica al usuario cuando el comprobante alcance "
    "los días restantes indicados antes de su vencimiento."))

    class Meta:
        verbose_name = _l("comprobante fiscal")
        verbose_name_plural = _l("comprobantes fiscales")
        ordering = ["company", "code"]
        constraints = [
            models.UniqueConstraint(fields=("company", "code"), 
                name="unique_code_for_company"),
            models.UniqueConstraint(fields=("company", "name"),
                name="unique_name_for_company")
        ]

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.strip(self.name).lower()

    @classmethod
    def validate_tax_receipt_number(cls, ncf: str, code: str=None) -> str:
        """Valida el formato del número de comprobante fiscal indicado."""
        try:
            ncf = ncf.upper()
        except (BaseException):
            raise ValidationError(_(f"El número de comprobante fiscal tiene un "
                f"formato no válido: '{ncf}'."))
        # Los números de comprobantes inicial y final del rango indicado,
        # deberán tener una longitud exacta de 11 caracteres, siendo el
        # primer caracter una letra entra A-Z, y el resto deberá ser solo númerico.
        if (len(ncf) != 11):
            raise ValidationError(_(f"El número de comprobante fiscal debe "
                f"tener 11 caracteres. Este tiene {len(ncf)} '{ncf}'."))

        # El primer caracter deberá ser una letra.
        letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if (not ncf[0] in letras):
            raise ValidationError(_(f"El primer caracter del comprobante fiscal "
                f"debe ser una letra comprendida en: '{letras}'. En cambio se "
                f"ha indicado {ncf[0]} '{ncf}'."))

        # La secuencia no puede ser solo ceros (0).
        if ncf[3:] == "00000000":
            raise ValidationError(_(f"No puede existir un comprobante con una "
                "secuencia igual a '000000000'. Si es el primer comprobante "
                "del rango deberá ser '000000001'."))

        # el restro de caracteres deberá ser solo numérico.
        try:
            int(ncf[1:])
        except (BaseException):
            raise ValidationError(_("La secuencia del comprobante tiene "
                f"caracteres no válidos ({ncf}). Solo el primer caracter debe "
                "ser una letra, el resto tiene que ser solo numérico."))

        if code != None:
            # Los tipos de comprobantes inicial y final del rango indicado,
            # deberán coincidir con el mismo tipo de comprobante de este registro.
            if (ncf[1:3] != code):
                raise ValidationError(_(f"El tipo de este comprobante fiscal "
                    f"'{ncf[1:3]}' no coincide con el tipo establecido "
                    f"'{code}'."))
        return ncf


class TaxReceiptNumber(utils.ModelBase):
    """
    Número de comprobante físcal (NCF).
    """

    company = None
    tags = None

    # Campo 'numero' es un string creado de la combinación:
    # serie + tipo.codigo + secuencia.
    number = models.CharField(_l("número"), max_length=11, editable=False)

    tax_receipt = models.ForeignKey(TaxReceipt, on_delete=models.PROTECT)

    serie = models.CharField(max_length=1)

    sequence = models.CharField(max_length=8,
    validators=[MinLengthValidator(8), MaxLengthValidator(8)])

    # Es null debido a la forma en que trabaja Unolet para crear los ncf a partir
    # de una AutorizacionNCF. La creación de los ncf se crean en la validación
    # de la AutorizacionNCF, y luego en AutorizacionNCF.save() se establece la
    # autorización a todos los ncf que se crearon para la misma.
    authorization = models.ForeignKey("finance.TaxReceiptAuthorization", 
    on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _l("número de comprobante fiscal")
        verbose_name_plural = _l("números de comprobantes fiscales")
        ordering = ["tax_receipt__company", "number"]
        constraints = [
            models.UniqueConstraint(fields=("tax_receipt", "number"), 
                name="unique_number_tax_receipt")
        ]
    
    def __str__(self):
        return self.number

    def clean(self):
        self.number = f"{self.serie}{self.tax_receipt.code}{self.sequence}"
        self.number = self.tax_receipt.validate_tax_receipt_number(self.number)


class TaxReceiptAuthorization(utils.ModelBase):
    """
    Registra nueva secuencia de Comprobante Fiscal.

    Autorización de NCF:​​ ​​​​Autorización de emisión de comprobantes fiscales para
    nuevos contribuyentes​. El proceso de autorización de emisión de comprobantes
    fiscales para nuevos contribuyentes o proceso de Altas de NCF, consiste en
    comprobar la veracidad de los datos de registro del contribuyente, tales
    como domicilio fiscal, actividad económica, etc., y a su vez comprobar si
    éste realiza operaciones comerciales.
    """

    # Establecemos un límite para el registro de los comprobantes fiscales.
    # debido a posibles limitaciones en el servidor, de modo que el límite 
    # de NCF en una autorización no puede exceder la cantidad máxima.
    # Hemos medido con timeit el tiempo cuando se indica exactamente un rango
    # de 50,000 comprobantes y el resultado arrojo 15 segundos aprox.
    # Este parece ser un límite apropiado.
    RECORD_LIMIT_FOR_AUTHORIZATION = 50000

    company = None # La empersa será tax_receipt.company}
    tags = None

    tax_receipt = models.ForeignKey(TaxReceipt, on_delete=models.PROTECT,
    verbose_name=_l("comprobante fiscal"))

    authorization = models.CharField(_l("autorización"), max_length=50,
    help_text=_l("número de autorización suministrado por el emisor de los "
    "comprobantes fiscales."))

    authorization_date = models.DateField(_l("fecha de autorización"),
    help_text=_l("fecha en que fueron autorizados estos comprobantes."))

    expiration_date = models.DateField(_l("fecha de vencimiento"),
    blank=True, null=True, help_text=_l("fecha en que vencerán estos números "
    "de comprobantes fiscales."))

    first_receipt = models.CharField(_l("comprobante inicial"),
    max_length=11, help_text=_l("número de comprobante inicial."))

    last_receipt = models.CharField(_l("comprobante final"), 
    max_length=11, help_text=_l("número de comprobante final."))

    class Meta:
        verbose_name = _l("autorización de comprobantes fiscales")
        verbose_name_plural = _l("autorizaciones de comprobantes fiscales")
        ordering = ["tax_receipt__company", "-authorization_date"]

    def __str__(self):
        return (f"{self.tax_receipt} "
            f"'{self.first_receipt}' -> '{self.last_receipt}'")

    def clean(self):
        # Una vez creada, no es posible modificarla.
        if self.pk:
            raise ValidationError(_("Esta autorización ya no se puede modificar."))

        # La fecha de autorización debe ser menor a la fecha de vencimiento.
        # De igual forma la fecha de vencimiento deberá ser una fecha futura.
        try:
            if (self.expiration_date < timezone.now().date()):
                raise ValidationError({"expiration_date": _("La fecha de "
                    "vencimiento debe ser una fecha futura.")})

            if (self.authorization_date > self.expiration_date):
                raise ValidationError({
                    "authorization_date": _("La fecha de la autorización debe "
                        "ser menor o igual a la fecha de vencimiento."),
                    "expiration_date": _("La fecha de vencimiento debe ser "
                    "mayor o igual a la fecha de autorización.")})
        except (TypeError, ValueError) as e:
            raise ValidationError("La fecha de vencimiento y/o fecha de "
                f"autorización no parecen ser fechas válidas. {e}") from e

        # Validamos el formato de los comprobantes que corresponden al rango.
        self.first_receipt = self.validate_tax_receipt_number(self.first_receipt)
        self.last_receipt = self.validate_tax_receipt_number(self.last_receipt)

        self.validate_tax_receipt_range()
        self.create_tax_receipts()

    def validate_tax_receipt_number(self, number: str) -> str:
        return self.tax_receipt.validate_tax_receipt_number(number)

    def validate_tax_receipt_range(self):
        """
        Valida que el rango de comprobantes esté correcto y no estén creados.
        """
        try:
            first = int(self.first_receipt[3:])
            last = int(self.last_receipt[3:])
        except (ValueError) as e:
            print(e)
            raise ValidationError(_("La secuencia debe ser numérica.")) from e

        if (first > last):
            raise ValidationError(_("El comprobante final debe ser mayor o "
                "igual al comprobante inicial."))
        # Establecemos un límite para el registro de los comprobantes fiscales.
        # debido a posibles limitaciones en el servidor, de modo que el límite 
        # de NCF en una autorización no puede exceder la cantidad máxima.
        if ((last - first + 1) > self.RECORD_LIMIT_FOR_AUTHORIZATION):
            raise ValidationError(_("La cantidad de NCFs a registrar "
            f"({last - first:,}) excede la cantidad máxima permitida para el "
            "registro de NCFs en una sola autorización. La cantidad máxima es "
            f"{self.RECORD_LIMIT_FOR_AUTHORIZATION:,}. Revise nuevamente el "
            "documento que contiene la autorización que intenta registrar. Si "
            "todo está correcto entonces comuníquese con Soporte Técnico para "
            "más información."))
        
    def create_tax_receipts(self):
        """Valida y crea los comprobantes del rango."""
        serie = self.first_receipt[0]
        try:
            first = int(self.first_receipt[3:])
            last = int(self.last_receipt[3:])
        except (ValueError) as e:
            print(e)
            raise ValidationError(_("La secuencia debe ser numérica.")) from e
        # Almacena los ids de los NCF que se van creando, 
        # para eliminarlos luego en caso de error.
        self._ids = []
        numbers_range = range(first, last + 1)
        for n in numbers_range:
            ncf = TaxReceiptNumber()
            ncf.serie = serie
            ncf.sequence = f"{n:>08}"
            ncf.tax_receipt = self.tax_receipt
            # ncf.authorization = self # la establecemos en el save()

            try:
                ncf.clean()
                ncf.save() # Guardamos para que Django valide UNIQUE.
            except (BaseException) as e:
                # En caso de algún error al crear un NCF, se eliminarán todos.
                try:
                    TaxReceiptNumber.objects.filter(id__in=self._ids).delete()
                except (BaseException) as e2:
                    e = f'{e}. {e2}'
                del self._ids

                raise ValidationError(_("Ha ocurrido un error intentando "
                    f"generar las secuencias de los comprobantes fiscales. "
                    f"'{e}'."))
            else:
                self._ids.append(ncf.id)

    def save(self, *args, **kwargs):
        if self._state.adding:
            # Establecemos esta autorización a los comprobantes ya creados.
            if getattr(self, "_ids", None):
                out = super().save(*args, **kwargs)
                qs = TaxReceiptNumber.objects.filter(id__in=self._ids)
                qs.update(authorization=self)
                del self._ids
            else:
                out = super().save(*args, **kwargs)
        else:
            out = super().save(*args, **kwargs)
        return out

    def is_used(self, tax_receipt_number: TaxReceiptNumber) -> bool:
        """Confirma si el comprobante ya ha sido utilizado."""
        try:
            tax_receipt_number.document # related_name
        except (models.ObjectDoesNotExist):
            return False
        return True

    def is_expired(self) -> bool:
        """Confirma si los comprobantes de esta autorización han vencido."""
        try:
            return self.expiration_date < timezone.now().date()
        except (TypeError):
            return self.expiration_date < timezone.now()

    def get_all_tax_receipt_number(self) -> models.QuerySet:
        """Obtiene un QuerySet con los objectos de esta autorización."""
        return TaxReceiptNumber.objects.filter(authorization=self)


class Transaction(utils.ModelBase):
    """
    Transacción contable.
    """

    DEBIT, CREDIT = "-", "+"
    MODE_CHOICES = (
        (DEBIT, _l("Débito")),
        (CREDIT, _l("Crédito")),
    )

    company = None # La empresa será document.doctype.company

    document = models.ForeignKey("document.Document", on_delete=models.CASCADE)

    # Determina si el monto se sumará o restará.
    # Esta idea es relativa para la empresa, de modo que un crédito será una 
    # entrada para la empresa y un débito una salida para la empresa.
    mode = models.CharField(_l("modo"), max_length=1, choices=MODE_CHOICES)

    amount = models.DecimalField(_l("monto"), max_digits=22, decimal_places=2,
    validators=[MinValueValidator(0)])

    concept = models.CharField(_l("concepto"), max_length=200, blank=True)

    create_user = models.ForeignKey("user.User", on_delete=models.PROTECT, 
    blank=True, null=True, default=None)

    note = models.CharField(_l("nota"), max_length=500, blank=True)

    class Meta:
        verbose_name = _l("transacción")
        verbose_name_plural = _l("transacciones")

    def __str__(self):
        if self.mode == self.DEBIT:
            return f"-{self.amount:,}"
        return f"{self.amount:,}"






