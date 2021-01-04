from django.test import TestCase

from company.tests.tests_models import get_or_create_company
from warehouse.models import Warehouse

def get_or_create_warehouse():
    warehouse = Warehouse(company=get_or_create_company(), name="test")
    warehouse.clean()
    warehouse.save()
    return warehouse