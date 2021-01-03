
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.views.generic import (TemplateView)
from base.middleware import (CheckUserInCompanyMiddleware, CompanyMiddleware)


class CheckUserInCompanyMiddlewareTestCase(TestCase):

    def setUp(self):
        pass


class CompanyMiddlewareTestCase(TestCase):
    
    def setUp(self):
        pass
