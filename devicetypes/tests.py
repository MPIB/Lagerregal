from __future__ import unicode_literals

from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse

import six
from model_mommy import mommy

from devicetypes.models import Type
from users.models import Lageruser


class TypeTests(TestCase):

    def setUp(self):
        '''method for setting up a client for testing'''
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_type_creation(self):
        '''method for testing the functionality of creating a new devicetype'''
        # creating an instance of Type and testing if created instance is instance of Type
        devicetype = mommy.make(Type)
        self.assertTrue(isinstance(devicetype, Type))

        # testing naming
        self.assertEqual(six.text_type(devicetype), devicetype.name)

        # testing creation of absolute and relative url
        self.assertEqual(devicetype.get_absolute_url(), reverse('type-detail', kwargs={'pk': devicetype.pk}))
        self.assertEqual(devicetype.get_edit_url(), reverse('type-edit', kwargs={'pk': devicetype.pk}))

    def test_type_list(self):
        '''method for testing the presentation and reachability of the list of devicestypes over several pages'''
        mommy.make(Type, _quantity=40)

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
