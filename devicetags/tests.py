import os.path


from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse

from devicetags.models import Devicetag
from users.models import Lageruser

class DevitagsTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser('test', 'test@test.com', 'test')
        self.client.login(username = 'test', password = 'test')

    def test_devicetag_creation(self):
        tag = mommy.make(Devicetag)
        self.assertEqual(tag.__unicode__(), tag.name)
        #there is no devicetag detail view
        self.assertEqual(tag.get_absolute_url(), reverse('devicetag-edit', kwargs={'pk': tag.pk}))
        self.assertEqual(tag.get_edit_url(), reverse('devicetag-edit', kwargs={'pk': tag.pk}))

    def test_devicetag_list(self):
        '''method for testing the presentation and reachability of the list of devicestags over several pages'''
        devicetags = mommy.make(Devicetag, _quantity=40)

        # testing if loading of devicetag-list-page was successful (statuscode 2xx)
        url = reverse("devicetag-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # testing the presentation of only 30 results of query on one page
        self.assertEqual(len(resp.context["devicetag_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)

        # testing the successful loading of second page of devicetag-list (statuscode 2xx)
        url = reverse("devicetag-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_devicetag_add(self):
        '''method for testing adding a devicetag'''
        devicetag = mommy.make(Devicetag)

        # testing successful loading of device-page of added device (statuscode 2xx)
        url = reverse("devicetag-add")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
