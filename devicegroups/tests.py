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

    def test_devicegroup_list(self):
        devicegroup = mommy.make(Devicegroup, _quantity=40)
        url = reverse("devicegroup-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["devicegroup_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("devicegroup-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_devicegroup_detail(self):
        devicegroup = mommy.make(Devicegroup)
        devicegroups = Devicegroup.objects.all()
        devicegroup = devicegroups[0]
        url = reverse("devicegroup-detail", kwargs={"pk": devicegroup.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_devicegroup_add(self):
        devicegroup = mommy.make(Devicegroup)
        url = reverse("devicegroup-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_devicegroup_edit(self):
        devicegroup = mommy.make(Devicegroup)
        devicegroups = Devicegroup.objects.all()
        devicegroup = devicegroups[0]
        url = reverse("devicegroup-edit", kwargs={"pk": devicegroup.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_devicegroup_delete(self):
        devicegroup = mommy.make(Devicegroup)
        devicegroups = Devicegroup.objects.all()
        devicegroup = devicegroups[0]
        url = reverse("devicegroup-delete", kwargs={"pk": devicegroup.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)