from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse

from network.models import IpAddress
from users.models import Lageruser


class IpAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", 'test')
        self.client.login(username="test", password="test")

    def test_ip_creation(self):
        ip = mommy.make(IpAddress)
        self.assertEqual(ip.__unicode__(), ip.address)
        self.assertEqual(ip.get_absolute_url(), reverse('ipaddress-detail', kwargs={'pk': ip.pk}))
