import os.path

from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse
from casper.tests import CasperTestCase

from devices.models import Device, Building, Room, Manufacturer, Template, Note
from users.models import Lageruser
from network.models import IpAddress


class DeviceTests(CasperTestCase):

    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_device_creation(self):
        device = mommy.make(Device)
        self.assertTrue(isinstance(device, Device))
        self.assertEqual(device.__unicode__(), device.name)
        self.assertEqual(device.get_absolute_url(), reverse('device-detail', kwargs={'pk': device.pk}))
        self.assertEqual(device.get_edit_url(), reverse('device-edit', kwargs={'pk': device.pk}))

    def test_device_list(self):
        devices = mommy.make(Device, _quantity=40)
        url = reverse("device-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["device_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("device-list", kwargs={"page":2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                '../casper-tests/device-list.js')))

    def test_device_detail(self):
        device = mommy.make(Device)
        ip = IpAddress(address = "127.0.0.1")
        ip.save()
        url = reverse("device-detail", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                '../casper-tests/device-detail.js')))

    def test_device_add(self):
        device = mommy.make(Device)
        url = reverse("device-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_device_edit(self):
        device = mommy.make(Device)
        url = reverse("device-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_device_delete(self):
        device = mommy.make(Device)
        url = reverse("device-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_device_archive(self):
        device = mommy.make(Device)
        archiveurl = reverse("device-archive", kwargs={"pk":1})
        resp = self.client.post(archiveurl)
        self.assertEqual(resp.status_code, 302)
        url = reverse("device-detail", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["device"].archived)

        resp = self.client.post(archiveurl)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.context["device"].archived)

    def test_device_trash(self):
        device = mommy.make(Device)
        trashurl = reverse("device-trash", kwargs={"pk":1})
        resp = self.client.post(trashurl)
        self.assertEqual(resp.status_code, 302)
        url = reverse("device-detail", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["device"].trashed)

        resp = self.client.post(trashurl)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.context["device"].trashed)

    def test_device_inventoried(self):
        device = mommy.make(Device)
        url = reverse("device-inventoried", kwargs={"pk":1})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        url = reverse("device-detail", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["device"].inventoried)

    def test_device_bookmark(self):
        device = mommy.make(Device)
        bookmarkurl = reverse("device-trash", kwargs={"pk":1})
        url = reverse("device-detail", kwargs={"pk":1})
        resp = self.client.post(bookmarkurl)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["device"].trashed)

        resp = self.client.post(bookmarkurl)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.context["device"].trashed)

    def test_device_ipaddress(self):
        device = mommy.make(Device)
        ip = IpAddress(address="127.0.0.1")
        ip.save()
        url = reverse("device-ipaddress", kwargs={"pk":1})
        resp = self.client.post(url, {"ipaddresses":[ip.pk], "device":device.pk})
        self.assertEqual(resp.status_code, 302)
        deviceurl = reverse("device-detail", kwargs={"pk":1})
        resp = self.client.get(deviceurl)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["device"].ipaddress_set.all()), 1)

        url = reverse("device-ipaddress-remove", kwargs={"pk":1, "ipaddress":1})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(deviceurl)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["device"].ipaddress_set.all()), 0)


class BuildingTests(CasperTestCase):

    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_building_creation(self):
        building = mommy.make(Building)
        self.assertTrue(isinstance(building, Building))
        self.assertEqual(building.__unicode__(), building.name)
        self.assertEqual(building.get_absolute_url(), reverse('building-detail', kwargs={'pk': building.pk}))
        self.assertEqual(building.get_edit_url(), reverse('building-edit', kwargs={'pk': building.pk}))

    def test_building_list(self):
        buildings = mommy.make(Building, _quantity=40)
        url = reverse("building-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["building_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("building-list", kwargs={"page":2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                '../casper-tests/generic-list.js'),
            basename="buildings"))

    def test_building_detail(self):
        building = mommy.make(Building)
        url = reverse("building-detail", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_building_add(self):
        building = mommy.make(Building)
        url = reverse("building-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_building_edit(self):
        building = mommy.make(Building)
        url = reverse("building-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_building_delete(self):
        building = mommy.make(Building)
        url = reverse("building-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class RoomTests(CasperTestCase):

    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_room_creation(self):
        room = mommy.make(Room)
        self.assertTrue(isinstance(room, Room))
        self.assertEqual(room.__unicode__(), room.name)
        self.assertEqual(room.get_absolute_url(), reverse('room-detail', kwargs={'pk': room.pk}))
        self.assertEqual(room.get_edit_url(), reverse('room-edit', kwargs={'pk': room.pk}))

    def test_room_list(self):
        rooms = mommy.make(Room, _quantity=40)
        url = reverse("room-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["room_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("room-list", kwargs={"page":2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                '../casper-tests/generictable-list.js'),
            basename="rooms"))

    def test_room_detail(self):
        room = mommy.make(Room)
        url = reverse("room-detail", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_room_add(self):
        room = mommy.make(Room)
        url = reverse("room-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_room_edit(self):
        room = mommy.make(Room)
        url = reverse("room-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_room_delete(self):
        room = mommy.make(Room)
        url = reverse("room-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class ManufacturerTests(CasperTestCase):

    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_manufacturer_creation(self):
        manufacturer = mommy.make(Manufacturer)
        self.assertTrue(isinstance(manufacturer, Manufacturer))
        self.assertEqual(manufacturer.__unicode__(), manufacturer.name)
        self.assertEqual(manufacturer.get_absolute_url(), reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        self.assertEqual(manufacturer.get_edit_url(), reverse('manufacturer-edit', kwargs={'pk': manufacturer.pk}))

    def test_manufacturer_list(self):
        manufacturers = mommy.make(Manufacturer, _quantity=40)
        url = reverse("manufacturer-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["manufacturer_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("manufacturer-list", kwargs={"page":2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                '../casper-tests/generic-list.js'),
            basename="manufacturers"))

    def test_manufacturer_detail(self):
        manufacturer = mommy.make(Manufacturer)
        url = reverse("manufacturer-detail", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_manufacturer_add(self):
        manufacturer = mommy.make(Manufacturer)
        url = reverse("manufacturer-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_manufacturer_edit(self):
        manufacturer = mommy.make(Manufacturer)
        url = reverse("manufacturer-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_manufacturer_delete(self):
        manufacturer = mommy.make(Manufacturer)
        url = reverse("manufacturer-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class TemplateTests(TestCase):

    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_template_creation(self):
        template = mommy.make(Template)
        self.assertTrue(isinstance(template, Template))
        self.assertEqual(template.__unicode__(), template.templatename)
        self.assertEqual(template.get_absolute_url(), reverse('device-list'))

    def test_template_list(self):
        templates = mommy.make(Template, _quantity=40)
        url = reverse("template-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["template_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("template-list", kwargs={"page":2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_template_add(self):
        template = mommy.make(Template)
        url = reverse("template-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_template_edit(self):
        template = mommy.make(Template)
        url = reverse("template-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_template_delete(self):
        template = mommy.make(Template)
        url = reverse("template-edit", kwargs={"pk":1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class NoteTests(TestCase):

    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_note_creation(self):
        note = mommy.make(Note)
        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.get_absolute_url(), reverse('device-detail', kwargs={'pk': note.device.pk}))
