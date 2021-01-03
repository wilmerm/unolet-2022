from django.test import TestCase
from django.urls import reverse

from user.models import User
from document.views import (DocumentUpdateView)
from document.tests.tests_models import get_or_create_document


class DocumentUpdateViewTest(TestCase):
    """Prueba para la vista DocumentUpdateView."""

    url_name = "document-document-update"

    def setUp(self):
        pass
        
    def test_get_absolute_url(self):
        """
        La url estará conformada por el pk de la empresa y el pk del documento.
        dicho pk de la empresa deberá ser el mismo que el pk de la empresa a la
        que pertence el documento.
        """
        document = get_or_create_document()
        url = reverse(self.url_name, 
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
        url = reverse(self.url_name, 
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
        url = reverse(self.url_name, kwargs={"company": 999, "pk": document.pk})

        self.client.login(username="test", password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_url_when_company_not_is_active(self):
        """Cuando el pk de la empresa en la url es una empresa inactiva."""
        document = get_or_create_document()
        company = document.doctype.company
        company.is_active = False
        company.save()
        url = reverse(self.url_name, 
            kwargs={"company": company.pk, "pk": document.pk})
        
        self.client.login(username="test", password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_post_save_is_ok(self):
        document = get_or_create_document()

        self.client.login(username="test", password="test")
        response = self.client.post(document.get_absolute_url())

        self.assertEqual(response.status_code, 200)


        




