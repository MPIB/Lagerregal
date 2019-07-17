from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from model_mommy import mommy

from network.models import IpAddress
from users.models import Lageruser


class IpAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Lageruser.objects.create_superuser("test", "test@test.com", 'test')
        self.client.login(username="test", password="test")

    def test_creation_view(self):
        address = mommy.make(IpAddress)
        self.assertTrue(isinstance(address, IpAddress))
        self.assertEqual(address.get_absolute_url(), reverse('ipaddress-detail', kwargs={'pk': address.pk}))

    def test_list_view(self):
        mommy.make(IpAddress, _quantity=40)

        # testing if loading of device-list-page was successful (statuscode 2xx)
        response = self.client.get('/ipaddresses/')
        self.assertEqual(response.status_code, 200)

        # testing the presentation of only 30 results of query on one page
        self.assertEqual(len(response.context["ipaddress_list"]), 30)
        self.assertEqual(response.context["paginator"].num_pages, 2)

        # testing the successful loading of second page of ipadresses-list (statuscode 2xx)
        response = self.client.get('/ipaddresses/?page=2')
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/ipaddresses/add/')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        address = mommy.make(IpAddress)
        response = self.client.get('/ipaddresses/%i/' % address.pk)
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        address = mommy.make(IpAddress)
        response = self.client.get('/ipaddresses/%i/edit/' % address.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        address = mommy.make(IpAddress)
        response = self.client.get('/ipaddresses/%i/delete/' % address.pk)
        self.assertEqual(response.status_code, 200)

    def test_user_view(self):
        response = self.client.get('/users/%i/ipaddress/' % self.admin.pk)
        self.assertEqual(response.status_code, 200)
