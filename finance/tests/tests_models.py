import timeit

from django.utils import timezone
from django.core.exceptions import ValidationError

from base.tests import BaseTestCase
from company.tests.tests_models import get_or_create_company
from finance.models import (Currency, TaxReceipt, TaxReceiptAuthorization, 
    TaxReceiptNumber)


class CurrencyModelTest(BaseTestCase):
    """Currency"""

    def test_first_currency_is_the_default_forever(self):
        """La primera moneda registrada siempre será la moneda default."""
        currency = Currency(company=get_or_create_company(), code="DOP", 
            symbol="RD$", name="PESO")
        currency.clean()
        currency.save()
        self.assertTrue(currency.is_default)
        self.assertEqual(currency.rate, 1)

    def test_only_one_is_default(self):
        """Solo podrá haber una moneda predeterminada."""
        currency1 = Currency(company=get_or_create_company(), code="DOP", 
            symbol="RD$", name="PESO")
        currency2 = Currency(company=get_or_create_company(), code="USD", 
            symbol="US$", name="DOLAR", is_default=True)
        currency1.save()
        currency2.save()
        self.assertTrue(currency1.is_default)
        self.assertFalse(currency2.is_default)


class TaxReceiptModelTest(BaseTestCase):
    """TaxReceipt"""

    def setUp(self):
        tax_receipt = TaxReceipt.objects.create(
            company=get_or_create_company(), 
            code="01", 
            name="test", 
            is_active=True,
            min_available_to_notify=5, 
            min_days_before_expiration_to_notify=5
        )

    def test_validate_tax_receipt_number_method(self):
        tax_receipt = TaxReceipt.objects.get(code="01")
        
        # Los números de comprobantes a continuación son inválidos:
        invalid_numbers = ["B01", "B0100000000", "B010000000", "B010000001",
            "B01000000001", "B010000000A", "100000001", "10000000001", 
            "1B0100000001", "1B010000001", "B01 00000001", "B01 0000001"]
        for number in invalid_numbers:
            self.assertRaises(ValidationError, 
                tax_receipt.validate_tax_receipt_number, ncf=number)
        
        # El siguiente comprobante es válido pero pertenece a un tipo diferente,
        # según su código 02, cuando intentamos validar uno con código 01.
        self.assertRaises(ValidationError, 
            tax_receipt.validate_tax_receipt_number, ncf="B0200000001", code="01")

        # Si todo marcha bien, el método debería devolver el mismo comprobante 
        # en mayúsculas.
        self.assertEqual(tax_receipt.validate_tax_receipt_number("b0100000009"), 
            "B0100000009")


class TaxReceiptAuthorizationModelTest(BaseTestCase):
    """TaxReceiptAuthorization"""

    def setUp(self):
        tax_receipt = TaxReceipt.objects.create(
            company=get_or_create_company(), 
            code="01", 
            name="test", 
            is_active=True,
            min_available_to_notify=5, 
            min_days_before_expiration_to_notify=5
        )
        self.authorization_unsaved = TaxReceiptAuthorization(
            tax_receipt=tax_receipt, 
            authorization="123456", 
            authorization_date=timezone.now().date(), 
            expiration_date=(timezone.now() + timezone.timedelta(days=5)).date(),
            first_receipt="B0100000001", 
            last_receipt="B0100000009"
        )

    def test_clean_method(self):
        # En la validación de la autorización se crearán los comprobantes.
        authorization = self.authorization_unsaved
        authorization.clean()

        # Según el rango indicado en setUp, deberían haberse creado 9 ncfs.
        count = authorization.get_all_tax_receipt_number().count()
        self.assertEqual(count, 9)

        # Nínguno de los comprobantes ha sido utilizado.
        for receipt in authorization.get_all_tax_receipt_number():
            self.assertFalse(authorization.is_used(receipt))

        # La autorización no ha expirado.
        self.assertFalse(authorization.is_expired())

        # Si llamamos a clean() nuevamente, se intentará crear los comprobantes
        # otra vez porque aun la autorización no se ha guardado. Pero los 
        # comprobantes ya fueron creados, entonces debería recibir un 
        # ValidationError.
        self.assertRaises(ValidationError, authorization.clean)

    def test_save_method(self):
        self.authorization_unsaved.clean()
        self.authorization_unsaved.save()

    def test_record_limit_for_authorization(self):
        """
        La variable RECORD_LIMIT_FOR_AUTHORIZATION en el modelo 
        TaxReceiptAuthorization establece la cantidad máxima de registros de 
        comprobantes que se pueden crear en cada autorización.
        """
        # El límite es de 50000, vamos a cambiarlo a solo 8, y en dicho caso 
        # deberiamos recibir un error ya que se van a crear 9 comprobantes.
        self.authorization_unsaved.RECORD_LIMIT_FOR_AUTHORIZATION = 8
        self.assertRaises(ValidationError, self.authorization_unsaved.clean)

    def test_efficiency_creating_tax_receipt_numbers(self):
        """Probamos el rendimiento al crear gran cantidad de comprobantes."""
        # Ya hicimos la prueba con 50,000 y tardó unos 15 segundos.
        # La prueba con 10,000 no debería pasar de 5 segundos.
        authorization = self.authorization_unsaved
        authorization.last_receipt = f"B0100010000"
        duration = timeit.timeit(authorization.clean, number=1)
        self.assertLess(duration, 5)

    def test_is_expired_method(self):
        """
        Prueba el método 'is_expired' que comprueba el vencimiento de los 
        comprobantes.
        """
        # Simulamos que los comprobantes vencieron ayer.
        authorization = self.authorization_unsaved
        authorization.expiration_date = timezone.now() - timezone.timedelta(days=1)
        authorization.save()
        self.assertTrue(authorization.is_expired())

    def test_is_used_method(self):
        """
        Prueba el método 'is_used' que comprueba si el comprobante que se 
        pasa como parámetro ha sido utilizado.
        """
        from document.tests.tests_models import get_or_create_document
        authorization = self.authorization_unsaved
        authorization.clean()
        authorization.save()
        # Hasta este punto ningún comprobante ha sido utilizado.
        for tax_receipt in authorization.get_all_tax_receipt_number():
            self.assertFalse(authorization.is_used(tax_receipt))
        # Simulamos que uno de los comprobantes ha sido utilizado.
        used_tax_receipt = authorization.get_all_tax_receipt_number()[0]
        unused_tax_receipt = authorization.get_all_tax_receipt_number()[1]
        document = get_or_create_document()
        document.tax_receipt_number = used_tax_receipt
        self.assertTrue(authorization.is_used(used_tax_receipt))
        self.assertFalse(authorization.is_used(unused_tax_receipt))

    




    