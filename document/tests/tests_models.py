from base.tests import BaseTestCase
from document.models import DocumentType, Document
from company.tests.tests_models import get_or_create_company
from warehouse.tests.tests_models import get_or_create_warehouse


def get_or_create_document():
    document = Document.objects.last()

    if not document:
        company = get_or_create_company()
        warehouse = get_or_create_warehouse()
        doctype = DocumentType(company=company, code="test", name="test")
        doctype.clean()
        doctype.save()
        document = Document(doctype=doctype, warehouse=warehouse)
        document.clean()
        document.save()
    return document


class DocumentModelTest(BaseTestCase):

    def setUp(self):
        self.document = get_or_create_document()

    def test_str_method(self, document=None, str_number="TEST-000000000001"):
        document = document or self.document
        self.assertEqual(str(document), str_number)

    def test_str_is_doctype_and_number_length_12_chars(self):
        """
        La salida de __str__ deberá ser igual a la suma del code del tipo de 
        documento, y el campo number rellenado hasta 12 caracter este último.
        """
        strout = "{}-{:0>12}".format(self.document.doctype, self.document.number)
        self.assertEqual(strout, str(self.document))
    
    def test_next_number(self):
        """El número debe ser secuencial y único para cada tipo de documento."""
        nextn = self.document.get_next_number_for_type(self.document.doctype)
        self.assertEqual(nextn, 2)
        document_2 = self.document
        document_2.number = 50007
        document_2.save()
        nextn = self.document.get_next_number_for_type(self.document.doctype)
        self.assertEqual(nextn, 50008)
        self.test_str_method(document_2, "TEST-000000050007")

    def test_calculate_method(self):
        dic = self.document.calculate()
        # Si existen diferencias entre los campos del documento y el resultado
        # calculado, entonces los campos serán actualizados por el método y 
        # devolver una clave 'updated' con valor True indicando que fueron 
        # actualizados, pero en este caso no esperamos ya que al guardar el 
        # movimiento ya se ejecutó document.calculate() en el movimiento...
        self.assertFalse(dic["updated"])
        self.assertEqual(dic["amount"], self.document.amount)
        self.assertEqual(dic["discount"], self.document.discount)
        self.assertEqual(dic["tax"], self.document.tax)
        self.assertEqual(dic["total"], self.document.total)
        # Si intentamos llamar otra vez el método la clave 'updated' sería False.
        dic = self.document.calculate()
        self.assertFalse(dic["updated"])

    

    
class DocumentTypeTest(BaseTestCase):

    def setUp(self):
        self.document = get_or_create_document()
    
    

    
    

