from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.client import Client

from model_mommy import mommy

from devices.models import Device
from users.models import Lageruser


class HistoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_global_view(self):
        response = self.client.get('/history/global/')
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        content_type = ContentType.objects.get(model='device')
        device = mommy.make(Device)
        response = self.client.get('/history/%i/%i/' % (content_type.pk, device.pk))
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        device = mommy.make(Device)
        response = self.client.post('/devices/%i/edit/' % device.pk, data={
            'name': 'test',
            'creator': self.admin.pk,
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/history/version/1/')
        self.assertEqual(response.status_code, 200)
