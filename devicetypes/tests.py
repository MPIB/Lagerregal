import os.path


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
        self.client.login(username = "test", password = "test")

    def test_type_creation(self):
        mytype = mommy.make(Type)
        self.assertEqual(mytype.__unicode__(), mytype.name)
        self.assertEqual(mytype.get_absolute_url(), reverse('type-detail', kwargs={'pk': mytype.pk}) )
        self.assertEqual(mytype.get_edit_url(), reverse('type-edit', kwargs={'pk': mytype.pk}) )

    def test_type_list(self):
        '''method for testing the presentation and reachability of the list of devicestypes over several pages'''
        devicetypes = mommy.make(Type, _quantity=40)

        # testing if loading of devicetype-list-page was successful (statuscode 2xx)
        url = reverse("type-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # testing the presentation of only 30 results of query on one page
        self.assertEqual(len(resp.context["type_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)

        # testing the successful loading of second page of devicetype-list (statuscode 2xx)
        url = reverse("type-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_type_detail(self):
        '''method for testing the reachability of existing devicetypes'''
        # querying all devices and choose first one to test
        devicetype = mommy.make(Type)
        devicetypes = Type.objects.all()
        devicetype = devicetypes[0]

        # test successful loading of detail-view of chossen devicetype (first one, statuscode 2xx)
        url = reverse("type-detail", kwargs={"pk": devicetype.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_type_add(self):
        '''method for testing adding a devicetype'''
        devicetype = mommy.make(Type)

        # testing successful loading of devicetype-page of added device (statuscode 2xx)
        url = reverse("type-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_type_edit(self):
        '''method for testing the functionality of editing a devicetype'''
        devicetype = mommy.make(Type)

        # querying all devicetypes and choose first one
        devicetypes = Type.objects.all()
        devicetype = devicetypes[0]

        # testing successful loading of edited devicetype-detail-page (statuscode 2xx)
        url = reverse("type-edit", kwargs={"pk": devicetype.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_type_delete(self):
        '''method for testing the functionality of deleting a devicetype'''
        devicetype = mommy.make(Type)

        # querying all devices and choose first one
        devicetypes = Type.objects.all()
        devicetype = devicetypes[0]

        # testing successful loading of devicetype-page after deletion (statuscode 2xx)
        url = reverse("type-edit", kwargs={"pk": devicetype.pk})
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)

class TypeAttributeTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username = "test", password = "test")

    def test_type_attribute_creation(self):
        attr = mommy.make(TypeAttribute)
        self.assertEqual(attr.__unicode__(), attr.name)
        self.assertEqual(attr.get_absolute_url(), reverse('type-detail', kwargs={'pk': attr.pk}) )

class TypeAttributeValueTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username = "test", password = "test")

    def test_attribute_value_creation(self):
        val = mommy.make(TypeAttributeValue)
        self.assertEqual(val.__unicode__(), val.value)
