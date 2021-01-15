
import copy

from django.core.exceptions import ValidationError

from base.tests import BaseTestCase
from person.models import Person, IdentificationType
from company.tests.tests_models import get_or_create_company


class IdentificationTypeModelTest(BaseTestCase):
    """Test para el modelo IdentificationType."""

    def test_clean_method(self):
        obj = IdentificationType(company=get_or_create_company(), name="test")
        obj.clean()

    def test_validate_unique_name_for_company(self):
        """El nombre es único para cada empresa."""
        obj1 = IdentificationType(company=get_or_create_company(), name="test")
        obj1.save()
        obj2 = IdentificationType(company=get_or_create_company(), name="test")
        self.assertRaises(ValidationError, obj2.clean)
        self.assertRaises(ValidationError, obj2.save)
        
    def test_validate_identification_method(self):
        obj = IdentificationType(
            company=get_or_create_company(), 
            name="test",
            characters="0123456789", # solo números.
            mode=IdentificationType.ALLOWED,
            min_length=9,
            max_length=11,
        )
        # Probamos con algunas identificaciones no acordes con la configuración.
        fakes = [
            "0", # min_length.
            "01234", # min_length 2
            "01234567891234" # max_length
            "0123456789a" # 'a' no permitido.
            "012345 123" # espacio no permitido.
        ]
        for fake in fakes:
            self.assertRaises(ValidationError, 
                obj.validate_identification, text=fake)

        # Estas si son válidas.
        valids = ["123456789", "1234567890", "12345678900"]
        for valid in valids:
            self.assertEqual(valid, obj.validate_identification(valid))


class PersonModelTest(BaseTestCase):
    """Test para el modelo Person."""

    def test_clean_identification_type_method(self):
        # La empresa para el tipo de identificación y la persona a la que se le
        # asigne, debe ser la misma empresa.
        company1 = get_or_create_company()
        company2 = copy.copy(company1)
        company2.pk = None
        company2.save()

        identification_type = IdentificationType.objects.create(
            company=company1, name="test")

        person = Person(company=company2, name="test", 
            identification="12345678901",
            identification_type=identification_type)

        self.assertRaises(ValidationError, person.clean)
        self.assertRaises(ValidationError, person.save)

        person.company = company1
        person.clean()
        


