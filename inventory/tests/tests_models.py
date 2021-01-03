import copy

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from company.tests import get_or_create_company
from document.tests.tests_models import get_or_create_document
from inventory.models import (Item, ItemFamily, ItemGroup, Movement)


class ItemTest(TestCase):
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


class ItemGroupTest(TestCase):
    def setUp(self):
        company = get_or_create_company()
        self.group = ItemGroup.objects.create(company=company, name="Group")

    def test_name_is_uppercase(self):
        self.assertEqual(self.group.name, "GROUP")
        

class ItemFamilyTest(TestCase):
    def setUp(self):
        company = get_or_create_company()
        self.family = ItemFamily.objects.create(company=company, name="Family")

    def test_name_is_uppercase(self):
        self.assertEqual(self.family.name, "FAMILY")


class MovementTest(TestCase):
    def setUp(self):
        pass
        document = get_or_create_document()
        item = Item.objects.create(company=document.doctype.company, name="item", 
            codename="item")

        self.quantity = 2
        self.price = 100.50
        self.discount = 10
        self.tax = 16
        self.movement = Movement(document=document, item=item, 
            quantity=self.quantity, price=self.price, discount=self.discount, 
            tax=self.tax)
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
        amount = (self.quantity * self.price) - self.discount
        self.assertEqual(amount, self.movement.get_amount())

    def test_get_total_method(self):
        total = ((self.quantity * self.price) - self.discount) + self.tax
        self.assertEqual(total, self.movement.get_total())


    

    
