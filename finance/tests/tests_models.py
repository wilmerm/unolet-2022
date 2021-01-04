from django.test import TestCase

from company.tests.tests_models import get_or_create_company
from finance.models import Currency


class CurrencyModelTest(TestCase):

    def test_first_currency_is_the_default_forever(self):
        """La primera moneda registra simpere será la moneda predeterminada."""
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


        