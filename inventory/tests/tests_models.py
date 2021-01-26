import copy
import timeit

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from base.tests import BaseTestCase
from company.tests.tests_models import get_or_create_company
from document.tests.tests_models import get_or_create_document
from inventory.models import (Item, ItemFamily, ItemGroup, Movement)
from finance.models import Tax


class ItemTest(BaseTestCase):

    def setUp(self):
        company = get_or_create_company()
        group = ItemGroup.objects.create(company=company, name="Group")
        family = ItemFamily.objects.create(company=company, name="Family")
        self.item = Item(codename="item", name="Item", company=company, 
            group=group, family=family)
        self.item.clean()
        self.item.save()

    def test_unique_item_for_company(self):
        item2 = Item.objects.create(codename="item", name="item", 
            company=self.item.company)
        item2.code = self.item.code
        self.assertRaises(IntegrityError, item2.save)

    def test_codename_is_uppercase(self):
        self.assertEqual(self.item.codename, "ITEM")

    def test_get_available_method(self):
        # Simulamos crear un documento de entrada con un movimiento de 10.
        input_document = copy.copy(get_or_create_document())
        input_doctype = copy.copy(input_document.doctype)
        input_doctype.pk = None
        input_doctype.code = "test2"
        input_doctype.generic = input_doctype.INVENTORY_INPUT # tipo entrada.
        input_doctype.save()
        input_document.pk = None
        input_document.doctype = input_doctype
        input_document.save()
        movement = Movement.objects.create(document=input_document, 
            item=self.item, quantity=10, price=0, discount=0, tax=0)
        self.assertEqual(self.item.get_available(input_document.warehouse), 10)

        # Modificamos la cantidad del movimiento a 15
        movement.quantity = 15
        movement.save()
        self.assertEqual(
            self.item.get_available(input_document.warehouse), 15)

        # Añadimos otro movimiento diferente con el mismo artículo con cantidad 3
        movement2 = copy.copy(movement)
        movement.pk = None
        movement.quantity = 3
        movement.save()
        self.assertEqual(
            self.item.get_available(input_document.warehouse), 18)

        # Simulamos crear un documento de salida con un movimiento de 4
        output_document = copy.copy(get_or_create_document())
        output_doctype = copy.copy(output_document.doctype)
        output_doctype.pk = None
        output_doctype.code = "test3"
        output_doctype.generic = output_doctype.INVENTORY_OUTPUT # de tipo salida.
        output_doctype.save()
        output_document.pk = None
        output_document.doctype = output_doctype
        output_document.save()
        movement = Movement.objects.create(document=output_document, 
            item=self.item, quantity=4, price=0, discount=0, tax=0)
        self.assertEqual(
            self.item.get_available(output_document.warehouse), 14)

        # Simulamos crear un documento que no afecta el inventario. la cantidad
        # será de 34 pero el disponible deberá seguir en 14 como el anterior.
        other_document = copy.copy(get_or_create_document())
        other_doctype = copy.copy(other_document.doctype)
        other_doctype.pk = None
        other_doctype.code = "test4"
        other_doctype.generic = other_doctype.PURCHASE_ORDER # No afecta el inventario.
        other_doctype.save()
        other_document.pk = None
        other_document.doctype = other_doctype
        other_document.save()
        movement = Movement.objects.create(document=other_document, 
            item=self.item, quantity=34, price=0, discount=0, tax=0)
        self.assertEqual(
            self.item.get_available(other_document.warehouse), 14)

        # Realizamos una transferencia entre almacenes, y transferimos 1 artículo.
        # en el almacén del documento se restará 1 que se sumará al nuevo 
        # almacén donde serán transferido.
        document = copy.copy(other_document)
        document.pk = None
        doctype = copy.copy(document.doctype)
        doctype.pk = None
        doctype.code = "TRANS"
        doctype.generic = document.doctype.__class__.TRANSFER
        doctype.save()
        document.doctype = doctype
        transfer_warehouse = copy.copy(document.warehouse)
        transfer_warehouse.pk = None
        transfer_warehouse.save()
        document.transfer_warehouse = transfer_warehouse
        document.save()
        movement = Movement.objects.create(document=document, item=self.item, 
            quantity=1, price=0, discount=0, tax=0)

        # -1 en el almacén de salida = 13.
        self.assertEqual(self.item.get_available(document.warehouse), 13)
        # +1 en el almacén de entrada = 1
        self.assertEqual(self.item.get_available(document.transfer_warehouse), 1)

         # Los artículos de servicio 'is_service == True' no afectan el inventaio.
        self.item.is_service = True
        self.assertEqual(self.item.get_available(), 0)

    def test_the_performance_of_the_get_available_method(self):
        """Probamos el rendimiento del método get_available."""
        document = copy.copy(get_or_create_document())
        doctype = copy.copy(document.doctype)
        doctype.pk = None
        doctype.code = "test5"
        doctype.generic = doctype.PURCHASE # Afecta el inv. como entrada.
        doctype.save()
        document.pk = None
        document.doctype = doctype
        document.save()
        # Vamos a crear muchos movimimientos.
        for n in range(10000):
            movement = Movement(document=document, 
                item=self.item, quantity=1, price=0, discount=0, tax=0)
            movement.save(not_calculate_document=True)
        # Ahora si, vamos a calcular los datos en el documento.
        self.assertLess(timeit.timeit(document.calculate, number=1), 0.5)
        # El método get_available en el movimiento depende del mismo en el item.
        self.assertLess(timeit.timeit(movement.get_available, number=1), 0.1)

        
class ItemGroupTest(BaseTestCase):
    def setUp(self):
        company = get_or_create_company()
        self.group = ItemGroup.objects.create(company=company, name="Group")

    def test_name_is_uppercase(self):
        self.assertEqual(self.group.name, "GROUP")
        

class ItemFamilyTest(BaseTestCase):
    def setUp(self):
        company = get_or_create_company()
        self.family = ItemFamily.objects.create(company=company, name="Family")

    def test_name_is_uppercase(self):
        self.assertEqual(self.family.name, "FAMILY")


class MovementTest(BaseTestCase):
    def setUp(self):
        document = get_or_create_document()
        item = Item.objects.create(company=document.doctype.company, 
            name="item", codename="item")

        self.quantity = 2
        self.price = 100.50
        self.discount = 10
        self.movement = Movement(document=document, item=item, 
            quantity=self.quantity, price=self.price, discount=self.discount)
        self.movement.clean()
        self.movement.save()

    def test_number(self):
        """La numeración seguirá una secuencia por cada documento."""
        self.assertEqual(self.movement.number, 1)
        movement2 = copy.copy(self.movement)
        movement2.pk = None
        movement2.number = None
        movement2.clean()
        movement2.save()
        self.assertEqual(movement2.number, 2)

    def test_get_amount_method(self):
        amount = (self.quantity * self.price)
        self.assertEqual(amount, self.movement.get_amount())

    def test_get_amount_with_discount_method(self):
        amount = (self.quantity * self.price) - self.discount
        self.assertEqual(amount, self.movement.get_amount_with_discount())

    def test_get_total_method(self):
        total = ((self.quantity * self.price) - self.discount) + 0
        self.assertEqual(total, self.movement.get_total())
        # Añadimos un impuesto al articulo.
        tax = Tax.objects.create(company=self.movement.document.doctype.company, 
            name="test", codename="test", value=18, value_type=Tax.PERCENT)
        self.movement.item.tax = tax
        self.movement.save()
        total = total + tax.calculate(total)
        self.assertEqual(total, self.movement.get_total())
        

    def test_get_local_amount_method(self):
        amount = (self.quantity * self.price)
        local_amount = amount * self.movement.document.currency_rate
        self.assertEqual(local_amount, self.movement.get_local_amount())

    def text_get_local_amount_with_discount_method(self):
        amount = (self.quantity * self.price) - self.discount
        amount = amount * self.movement.document.currency_rate
        self.assertEqual(amount, self.movement.get_local_amount_with_discount())

    def test_get_local_total_method(self):
        total = ((self.quantity * self.price) - self.discount) + self.movement.tax
        local_total = total * self.movement.document.currency_rate
        self.assertEqual(local_total, self.movement.get_local_total())

    def test_document_company_is_item_company(self):
        """La empresa del documento debe ser la misma que la del artículo."""
        company2 = copy.copy(self.movement.item.company)
        company2.pk = None
        company2.save()
        self.movement.document.doctype.company = company2
        self.assertRaises(ValidationError, self.movement.save)



    

    
