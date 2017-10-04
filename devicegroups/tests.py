import os.path


from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse

from devicegroups.models import Devicegroup
from users.models import Lageruser

class DevicegroupTests(TestCase):
    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username = 'test', password = 'test')

    def test_devicegroup_creation(self):
        devicegroup = mommy.make(Devicegroup)
        self.assertEqual(devicegroup.__unicode__(), devicegroup.name)
        self.assertEqual(devicegroup.get_absolute_url(), reverse('devicegroup-detail', kwargs={'pk': devicegroup.pk}) )
        self.assertEqual(devicegroup.get_edit_url(), reverse('devicegroup-edit', kwargs={'pk': devicegroup.pk}))
