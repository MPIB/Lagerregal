from django.utils import unittest
from django.test.client import Client
from django.test import TestCase
from models import Device, Building, Room, Manufacturer, Template, Note
from users.models import Lageruser
from django.utils import timezone
from model_mommy import mommy
from django.core.urlresolvers import reverse

class DeviceTests(TestCase):

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
        devices = mommy.make(Device, _quantity=20)
        url = reverse("device-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["device_list"]), 20)

class BuildingTests(TestCase):

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

class RoomTests(TestCase):

    def test_room_creation(self):
        room = mommy.make(Room)
        self.assertTrue(isinstance(room, Room))
        self.assertEqual(room.__unicode__(), room.name)
        self.assertEqual(room.get_absolute_url(), reverse('room-detail', kwargs={'pk': room.pk}))
        self.assertEqual(room.get_edit_url(), reverse('room-edit', kwargs={'pk': room.pk}))

class ManufacturerTests(TestCase):

    def test_manufacturer_creation(self):
        manufacturer = mommy.make(Manufacturer)
        self.assertTrue(isinstance(manufacturer, Manufacturer))
        self.assertEqual(manufacturer.__unicode__(), manufacturer.name)
        self.assertEqual(manufacturer.get_absolute_url(), reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        self.assertEqual(manufacturer.get_edit_url(), reverse('manufacturer-edit', kwargs={'pk': manufacturer.pk}))

class TemplateTests(TestCase):

    def test_template_creation(self):
        template = mommy.make(Template)
        self.assertTrue(isinstance(template, Template))
        self.assertEqual(template.__unicode__(), template.templatename)
        self.assertEqual(template.get_absolute_url(), reverse('device-list'))

class NoteTests(TestCase):

    def test_note_creation(self):
        note = mommy.make(Note)
        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.get_absolute_url(), reverse('device-detail', kwargs={'pk': note.device.pk}))