
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.views.generic import (TemplateView)
from base.middleware import (CheckUserInCompanyMiddleware, CompanyMiddleware)


class BaseTestCase(TestCase):
    """
    Clase base de la cual herederán las demás clases de prueba.
    """

    def setUp(self):
        from company.models import CompanyPermission
        CompanyPermission.populate()


class CheckUserInCompanyMiddlewareTestCase(BaseTestCase):

    def setUp(self):
        pass


class CompanyMiddlewareTestCase(BaseTestCase):
    
    def setUp(self):
        pass
