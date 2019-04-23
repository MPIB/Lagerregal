from django.test.client import Client
from django.test import TestCase
from django.urls import reverse

import six
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
        self.assertEqual(six.text_type(devicegroup), devicegroup.name)
        self.assertEqual(devicegroup.get_absolute_url(), reverse('devicegroup-detail', kwargs={'pk': devicegroup.pk}))
        self.assertEqual(devicegroup.get_edit_url(), reverse('devicegroup-edit', kwargs={'pk': devicegroup.pk}))
