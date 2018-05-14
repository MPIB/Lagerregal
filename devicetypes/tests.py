from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse

from devicetypes.models import Type, TypeAttribute, TypeAttributeValue
from users.models import Lageruser


class TypeTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_type_creation(self):
        mytype = mommy.make(Type)
        self.assertEqual(mytype.__unicode__(), mytype.name)
        self.assertEqual(mytype.get_absolute_url(), reverse('type-detail', kwargs={'pk': mytype.pk}))
        self.assertEqual(mytype.get_edit_url(), reverse('type-edit', kwargs={'pk': mytype.pk}))


class TypeAttributeTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_type_attribute_creation(self):
        attr = mommy.make(TypeAttribute)
        self.assertEqual(attr.__unicode__(), attr.name)
        self.assertEqual(attr.get_absolute_url(), reverse('type-detail', kwargs={'pk': attr.pk}))


class TypeAttributeValueTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_attribute_value_creation(self):
        val = mommy.make(TypeAttributeValue)
        self.assertEqual(val.__unicode__(), val.value)
