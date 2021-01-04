from django.urls import reverse

from base.tests import BaseTestCase
from user.tests.tests_models import get_or_create_user
from warehouse.tests.tests_models import get_or_create_warehouse
from warehouse.views import (WarehouseDetailView, WarehouseListView)


class WarehouseDetailViewTest(BaseTestCase):
    """Test para la vista WarehouseDetailView."""

    url_name = "warehouse-warehouse-detail"
    view_class = WarehouseDetailView
    company_permission_required = view_class.company_permission_required

    def test_user_not_has_company_permission_required(self):
        """
        Cuando el usuario no tiene el permiso de empresa que requiere la vista.
        """
        user = get_or_create_user()
        warehouse = get_or_create_warehouse()
        self.client.login(username="test", password="test")
        response = self.client.get(warehouse.get_absolute_url())
        self.assertEqual(response.status_code, 403)

    def test_user_has_company_permission_required(self):
        """Cuando el usuario tiene el permiso que requiere la vista."""
        user = get_or_create_user()
        warehouse = get_or_create_warehouse()
        
        user.assign_company_permission(
            self.company_permission_required, warehouse.company)

        self.client.login(username="test", password="test")
        response = self.client.get(warehouse.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_user_has_company_permission_required_but_not_in_company(self):
        """El usuario tiene los permisos, pero no pertenece a la empresa."""
        user = get_or_create_user()
        warehouse = get_or_create_warehouse()
        warehouse.company.users.remove(user)

        user.assign_company_permission(
            self.company_permission_required, warehouse.company)

        self.client.login(username="test", password="test")
        response = self.client.get(warehouse.get_absolute_url())
        self.assertEqual(response.status_code, 404)
