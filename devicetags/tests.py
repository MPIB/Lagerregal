from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from model_mommy import mommy

from devices.models import Device
from devicetags.models import Devicetag
from users.models import Lageruser


class DevicetagsTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', 'test')
        self.client.login(username='test', password='test')

    def test_devicetag_creation(self):
        tag = mommy.make(Devicetag)
        self.assertEqual(str(tag), tag.name)
        # there is no devicetag detail view
        self.assertEqual(tag.get_absolute_url(), reverse('devicetag-edit', kwargs={'pk': tag.pk}))
        self.assertEqual(tag.get_edit_url(), reverse('devicetag-edit', kwargs={'pk': tag.pk}))

    def test_list_view(self):
        response = self.client.get('/devicetags/')
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/devicetags/add/')
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        tag = mommy.make(Devicetag)
        response = self.client.get('/devicetags/%i/edit/' % tag.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        tag = mommy.make(Devicetag)
        response = self.client.get('/devicetags/%i/delete/' % tag.pk)
        self.assertEqual(response.status_code, 200)

    def test_devicetags_view(self):
        device = mommy.make(Device)
        tag = mommy.make(Devicetag)
        device.tags.add(tag)
        response = self.client.get('/devices/%i/tags/' % tag.pk)
        self.assertEqual(response.status_code, 200)

    def test_remove_view(self):
        device = mommy.make(Device)
        tag = mommy.make(Devicetag)
        device.tags.add(tag)
        response = self.client.get('/devices/%i/tags/%i/' % (device.pk, tag.pk))
        self.assertEqual(response.status_code, 200)
