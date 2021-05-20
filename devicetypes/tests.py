from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from model_mommy import mommy

from devicetypes.models import Type
from users.models import Lageruser


class TypeTests(TestCase):

    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_type_creation(self):
        devicetype = mommy.make(Type)
        self.assertTrue(isinstance(devicetype, Type))
        self.assertEqual(str(devicetype), devicetype.name)
        self.assertEqual(devicetype.get_absolute_url(), reverse('type-detail', kwargs={'pk': devicetype.pk}))
        self.assertEqual(devicetype.get_edit_url(), reverse('type-edit', kwargs={'pk': devicetype.pk}))

    def test_list_view(self):
        mommy.make(Type, _quantity=40)
        response = self.client.get('/types/')
        self.assertEqual(response.status_code, 200)

        # testing the presentation of only 30 results of query on one page
        self.assertEqual(len(response.context["type_list"]), 30)
        self.assertEqual(response.context["paginator"].num_pages, 2)

        # testing the successful loading of second page of devicetype-list (statuscode 2xx)
        response = self.client.get('/types/?page=2')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        devicetype = mommy.make(Type)
        response = self.client.get('/types/%i/' % devicetype.pk)
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/types/add/')
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        devicetype = mommy.make(Type)
        response = self.client.get('/types/%i/edit/' % devicetype.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        devicetype = mommy.make(Type)
        response = self.client.get('/types/%i/delete/' % devicetype.pk)
        self.assertEqual(response.status_code, 200)

    def test_merge_view(self):
        devicetype1 = mommy.make(Type)
        devicetype2 = mommy.make(Type)
        response = self.client.get('/types/%i/merge/%i/' % (devicetype1.pk, devicetype2.pk))
        self.assertEqual(response.status_code, 200)
