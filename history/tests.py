from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse

from devices.models import Device, Building, Room, Manufacturer, Template, Note
from users.models import Lageruser
from network.models import IpAddress
from reversion.models import Version


class HistoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_history_detail(self):
        mommy.make(Device)
        devices = Device.objects.all()
        device = devices[0]
        url = reverse("device-edit", kwargs={"pk": device.pk})
        resp = self.client.post(url, data={"name": "test", "creator": self.admin.pk})
        self.assertEqual(resp.status_code, 302)

        url = reverse("history-detail", kwargs={"pk": 1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)