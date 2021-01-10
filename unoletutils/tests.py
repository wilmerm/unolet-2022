from django.test import TestCase
from django.urls import reverse

from user.tests.tests_models import get_or_create_user
from company.tests.tests_models import get_or_create_company
from warehouse.models import Warehouse


class ViewDecoratorTest(TestCase):
    """
    Test para 'unoletutils.libs.utils.view_decorator'.

    Este decorador se utilizará para decorar las vistas de Unolet.
    """

    def setUp(self):
        user = get_or_create_user()
        company = get_or_create_company()
        company.users.add(user)

    def test_form_valid(self):
        """
        El decorador view_decorator decora el método de la vista 'form_valid',
        cuando se está creando un objeto y el modelo en cuestión contiene los 
        campos 'create_user' y/o 'company', sus valores se establecen en este 
        método decorado.
        """
        # Un almacén contiene un campo 'company', vamos a simular crear uno y el 
        # campo 'company' deberá establecerse de forma automática.
        self.client.login(username="test", password="test")

        # Hasta este punto no hay almacenes registrados.
        self.assertEqual(Warehouse.objects.count(), 0)
    
        response = self.client.post(
            reverse('warehouse-warehouse-create', kwargs={"company": 1}),
                data={"name": "test"})

        # La respuesta debe ser 302 redirecionamiento.
        self.assertEqual(response.status_code, 302)

        # Debió haberse creado un almacén.
        self.assertEqual(Warehouse.objects.count(), 1)

        # el almacén deberá tener el campo 'company' con la empresa actual.
        warehouse = Warehouse.objects.get(name="test")
        self.assertEqual(warehouse.company.pk, 1)
        

        
        

