from django.test import TestCase

from user.tests.tests_models import get_or_create_user
from .models import Company


def get_or_create_company():
    company = Company.objects.last()
    if not company:
        company = Company(name="Test", business_name="Test")
        company.clean()
        company.save()
        company.users.add(get_or_create_user())
    return company
