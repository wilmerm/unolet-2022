from django.test import TestCase
from document.models import DocumentType, Document
from company.tests.tests_models import get_or_create_company


def get_or_create_document():
    document = Document.objects.last()

    if not document:
        company = get_or_create_company()
        doctype = DocumentType(company=company, code="type01", 
            name="Tipo de documento de prueba")
        doctype.clean()
        doctype.save()
        document = Document(doctype=doctype)
        document.clean()
        document.save()

    return document


class DocumentModelTest(TestCase):

    def setUp(self):
        self.document = get_or_create_document()

    def test_str_method(self, document=None, str_number="TYPE01-000000000001"):
        document = document or self.document
        self.assertEqual(str(document), str_number)

    def test_str_is_doctype_and_number_length_12_chars(self):
        # La salida de __str__ deberá ser igual a la suma del code del tipo de 
        # documento, y el campo number rellenado hasta 12 caracter este último.
        strout = "{}-{:0>12}".format(self.document.doctype, self.document.number)
        self.assertEqual(strout, str(self.document))
    
    def test_next_number(self):
        # El número debe ser secuencial y único para cada tipo de documento.
        nextn = self.document._get_next_number_for_type(self.document.doctype)
        self.assertEqual(nextn, 2)
        document_2 = self.document
        document_2.number = 50007
        document_2.save()
        nextn = self.document._get_next_number_for_type(self.document.doctype)
        self.assertEqual(nextn, 50008)
        self.test_str_method(document_2, "TYPE01-000000050007")

    
class DocumentTypeTest(TestCase):

    def setUp(self):
        self.document = get_or_create_document()
    
    

    
    

