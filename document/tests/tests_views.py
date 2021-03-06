from django.test import TestCase
from django.urls import reverse, reverse_lazy

from user.models import User
from document.models import Document
from user.tests.tests_models import get_or_create_user
from document.tests.tests_models import get_or_create_document
from warehouse.tests.tests_models import get_or_create_warehouse


class DocumentUpdateViewTest(TestCase):
    """Prueba para la vista DocumentUpdateView."""

    def setUp(self):
        self.url_name = "document-document-{generictype}-update"
        
    def test_get_absolute_url(self):
        """
        La url estará conformada por el pk de la empresa y el pk del documento.
        dicho pk de la empresa deberá ser el mismo que el pk de la empresa a la
        que pertence el documento.
        """
        document = get_or_create_document()

        url = reverse(
            self.url_name.format(generictype=document.doctype.generic),
            kwargs={"company": document.doctype.company.id, "pk": document.pk})

        self.assertEqual(url, document.get_absolute_url())

    def test_url_company_not_is_document_company(self):
        """
        Si se intenta acceder al detalle de un documento fuera de la empresa a 
        la que pertence deberá lanzar un código de error.

        Por ejempo tenemos la url: 'company/company/3/document/document/88/...'
        - company.pk = 3
        - document.pk = 88

        Entonces document.doctype.company.pk deberá ser igual a 3, de lo 
        contrario estariamos dentro de una empresa a la que no pertenece el 
        documento en cuestión y devolverá un status_code = 404.
        """
        document = get_or_create_document()
        # Creamos una secunda compañia a la que no pertenecerá el documento.
        company_2 = document.doctype.company
        company_2.pk = None
        company_2.clean()
        company_2.save()
        # Esta url no será válida porque el documento no pertenece a esa empresa.
        url = reverse(
            self.url_name.format(generictype=document.doctype.generic), 
            kwargs={"company": company_2.pk, "pk": document.pk})

        self.client.login(username="test", password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_url_when_company_does_not_exist(self):
        """
        Cuando el pk de la empresa en la url es de una empresa que no existe.
        """
        document = get_or_create_document()
        # No exite una empresa con pk = 999
        url = reverse(
            self.url_name.format(generictype=document.doctype.generic), 
            kwargs={"company": 999, "pk": document.pk})

        self.client.login(username="test", password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_url_when_company_not_is_active(self):
        """Cuando el pk de la empresa en la url es una empresa inactiva."""
        document = get_or_create_document()
        company = document.doctype.company
        company.is_active = False
        company.save()
        url = reverse(
            self.url_name.format(generictype=document.doctype.generic), 
            kwargs={"company": company.pk, "pk": document.pk})
        
        self.client.login(username="test", password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_post_save_is_ok(self):
        document = get_or_create_document()
        document.doctype.company.users.add(get_or_create_user())
        self.client.login(username="test", password="test")

        response = self.client.post(
            reverse(f"document-document-{document.doctype.generic}-create", 
            kwargs={"company": document.doctype.company.id}),
            data={"warehouse": document.warehouse.pk, 
                "doctype": document.doctype.pk,
                "note": "test_doc_1"})
        self.assertEqual(response.status_code, 200)


        




