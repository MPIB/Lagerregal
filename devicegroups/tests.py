from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from model_mommy import mommy

from devicegroups.models import Devicegroup
from users.models import Lageruser


class DevicegroupTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username='test', password='test')

    def test_devicegroup_creation(self):
        devicegroup = mommy.make(Devicegroup)
        self.assertEqual(str(devicegroup), devicegroup.name)
        self.assertEqual(devicegroup.get_absolute_url(), reverse('devicegroup-detail', kwargs={'pk': devicegroup.pk}))
        self.assertEqual(devicegroup.get_edit_url(), reverse('devicegroup-edit', kwargs={'pk': devicegroup.pk}))

    def test_list_view(self):
        response = self.client.get('/devicegroups/')
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/devicegroups/add/')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        devicegroup = mommy.make(Devicegroup)
        response = self.client.get('/devicegroups/%i/' % devicegroup.pk)
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        devicegroup = mommy.make(Devicegroup)
        response = self.client.get('/devicegroups/%i/edit/' % devicegroup.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        devicegroup = mommy.make(Devicegroup)
        response = self.client.get('/devicegroups/%i/delete/' % devicegroup.pk)
        self.assertEqual(response.status_code, 200)
