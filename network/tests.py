from __future__ import unicode_literals

from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse

from users.models import Lageruser
from network.models import IpAddress


class IpAddressTests(TestCase):
    def setUp(self):
        '''method for setting up a client for testing'''
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", 'test')
        self.client.login(username="test", password="test")

    def test_IpAddress_creation(self):
        '''method for testing the functionality of creating a new IpAddress'''
        # creating an instance of IpAddress and testing if created instance is instance of IpAddress
        address = mommy.make(IpAddress)
        self.assertTrue(isinstance(address, IpAddress))

        # testing creation of absolute and relative url
        self.assertEqual(address.get_absolute_url(), reverse('ipaddress-detail', kwargs={'pk': address.pk}))

    def test_IpAddress_list(self):
        '''method for testing the presentation and reachability of the list of IpAdresses over several pages'''
        address = mommy.make(IpAddress, _quantity=40)

        # testing if loading of device-list-page was successful (statuscode 2xx)
        url = reverse("ipaddress-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # testing the presentation of only 30 results of query on one page
        self.assertEqual(len(resp.context["ipaddress_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)

        # testing the successful loading of second page of ipadresses-list (statuscode 2xx)
        url = reverse("ipaddress-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_IpAddress_detail(self):
        '''method for testing the reachability of existing devices'''
        # querying all devices and choose first one to test
        address = mommy.make(IpAddress)
        addresses = IpAddress.objects.all()
        address = addresses[0]

        # test successful loading of detail-view of chossen IpAddress (first one, statuscode 2xx)
        url = reverse("ipaddress-detail", kwargs={"pk": address.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_IpAddress_add(self):
        '''method for testing adding a Ipaddress'''
        address = mommy.make(IpAddress)

        # testing successful loading of Ipaddress-page of added device (statuscode 2xx)
        url = reverse("ipaddress-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_IpAddress_edit(self):
        '''method for testing the functionality of editing a IpAddress'''
        address = mommy.make(IpAddress)

        # querying all devices and choose first one
        addresses = IpAddress.objects.all()
        address = addresses[0]

        # testing successful loading of edited ipaddress-detail-page (statuscode 2xx)
        url = reverse("ipaddress-edit", kwargs={"pk": address.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_IpAddress_delete(self):
        '''method for testing the functionality of deleting a IpAddress'''
        address = mommy.make(IpAddress)

        # querying all devices and choose first one
        addresses = IpAddress.objects.all()
        address = addresses[0]

        # testing successful loading of ipaddress-page after deletion (statuscode 2xx)
        url = reverse("ipaddress-edit", kwargs={"pk": address.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
