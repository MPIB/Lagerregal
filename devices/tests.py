from datetime import datetime, timedelta

from django.test.client import Client
from django.test import TestCase
from django.urls import reverse

from model_mommy import mommy

from devices.models import Device, Building, Room, Manufacturer, Template, Note, Lending, DeviceInformationType, DeviceInformation, Picture
from users.models import Lageruser
from network.models import IpAddress


class DeviceTests(TestCase):

    def setUp(self):
        '''method for setting up a client for testing'''
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_device_creation(self):
        '''method for testing the functionality of creating a new device'''
        device = mommy.make(Device)
        lending_past = mommy.make(Lending, duedate=(datetime.today() - timedelta(days=1)).date())
        lending_future = mommy.make(Lending, duedate=(datetime.today() + timedelta(days=1)).date())
        self.assertTrue(isinstance(device, Device))
        self.assertEqual(str(device), device.name)
        self.assertEqual(device.get_absolute_url(), reverse('device-detail', kwargs={'pk': device.pk}))
        self.assertEqual(device.get_edit_url(), reverse('device-edit', kwargs={'pk': device.pk}))
        self.assertEqual(device.get_as_dict(), {
            "name": device.name,
            "description": device.description,
            "manufacturer": device.manufacturer,
            "devicetype": device.devicetype,
            "room": device.room,
        })
        self.assertFalse(device.is_overdue())
        self.assertTrue(mommy.make(Device, currentlending=lending_past).is_overdue())
        self.assertFalse(mommy.make(Device, currentlending=lending_future).is_overdue())

    def test_list_view(self):
        mommy.make(Device, _quantity=40)

        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["device_list"]), 30)
        self.assertEqual(response.context["paginator"].num_pages, 2)

        response = self.client.get('/devices/page/2')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        device = mommy.make(Device)
        response = self.client.get('/devices/%i/' % device.pk)
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        device = mommy.make(Device, name="used")

        response = self.client.get('/devices/add')
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        data = form.initial
        data['uses'] = device.id
        data['name'] = "uses"
        response = self.client.post('/devices/add', data)
        device.refresh_from_db()
        self.assertEqual(device.used_in.name, 'uses')

    def test_update_view(self):
        device = mommy.make(Device)
        response = self.client.get('/devices/%i/edit/' % device.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        device = mommy.make(Device)
        response = self.client.get('/devices/%i/delete/' % device.pk)
        self.assertEqual(response.status_code, 200)

    def test_archive_view(self):
        device = mommy.make(Device, archived=None)

        response = self.client.post('/devices/%i/archive/' % device.pk)
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertIsNotNone(device.archived)

        response = self.client.post('/devices/%i/archive/' % device.pk)
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertIsNone(device.archived)

    def test_trash_view(self):
        device = mommy.make(Device, trashed=None)

        response = self.client.post('/devices/%i/trash/' % device.pk)
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertIsNotNone(device.trashed)

        response = self.client.post('/devices/%i/trash/' % device.pk)
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertIsNone(device.trashed)

    def test_trash_view_sets_child_used_in_to_none(self):
        device = mommy.make(Device)
        used_device = mommy.make(Device, used_in=device)
        self.client.post('/devices/%i/trash/' % device.pk)
        used_device.refresh_from_db()
        self.assertIsNone(used_device.used_in)

    def test_trash_view_sets_self_used_in_to_none(self):
        device = mommy.make(Device, _fill_optional=['used_in'])
        self.client.post('/devices/%i/trash/' % device.pk)
        device.refresh_from_db()
        self.assertIsNone(device.used_in)

    def test_trash_view_returns_lending(self):
        lending = mommy.make(Lending, _fill_optional=['device', 'owner'])
        lending.device.currentlending = lending
        lending.device.save()
        self.client.post('/devices/%i/trash/' % lending.device.pk)
        lending.refresh_from_db()
        self.assertIsNotNone(lending.returndate)

    def test_inventoried_view(self):
        device = mommy.make(Device)
        response = self.client.post('/devices/%i/inventoried/' % device.pk)
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertIsNotNone(device.inventoried)

    def test_bookmark_view(self):
        device = mommy.make(Device)

        response = self.client.post('/devices/%i/bookmark/' % device.pk)
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertEqual(device.bookmarkers.count(), 1)

        response = self.client.post('/devices/%i/bookmark/' % device.pk)
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertEqual(device.bookmarkers.count(), 0)

    def test_ipaddress_view(self):
        device = mommy.make(Device)
        ip = mommy.make(IpAddress)

        response = self.client.post('/devices/%i/ipaddress/' % device.pk, {
            'ipaddresses': [ip.pk],
            'device': device.pk,
        })
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertEqual(device.ipaddress_set.count(), 1)

        response = self.client.post('/devices/%i/ipaddress/%i/remove' % (device.pk, ip.pk))
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertEqual(device.ipaddress_set.count(), 0)

    def test_lending_list_view(self):
        lending = mommy.make(Lending)
        device = mommy.make(Device, currentlending=lending)
        response = self.client.get('/devices/%i/lending/' % device.pk)
        self.assertEqual(response.status_code, 200)

    def test_lend_view(self):
        response = self.client.post('/devices/lend/')
        self.assertEqual(response.status_code, 200)

    def test_return_view_device(self):
        device = mommy.make(Device)
        lending = mommy.make(Lending, device=device)
        response = self.client.post('/devices/return/%i' % lending.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_view_user(self):
        user = mommy.make(Lageruser)
        lending = mommy.make(Lending, owner=user)
        response = self.client.post('/devices/return/%i' % lending.pk)
        self.assertEqual(response.status_code, 302)


class BuildingTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_building_creation(self):
        building = mommy.make(Building)
        self.assertTrue(isinstance(building, Building))
        self.assertEqual(str(building), building.name)
        self.assertEqual(building.get_absolute_url(), reverse('building-detail', kwargs={'pk': building.pk}))
        self.assertEqual(building.get_edit_url(), reverse('building-edit', kwargs={'pk': building.pk}))

    def test_list_view(self):
        mommy.make(Building, _quantity=40)

        response = self.client.get('/buildings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["building_list"]), 30)
        self.assertEqual(response.context["paginator"].num_pages, 2)

        response = self.client.get('/buildings/2')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        building = mommy.make(Building)
        response = self.client.get('/buildings/view/%i' % building.pk)
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/buildings/add')
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        building = mommy.make(Building)
        response = self.client.get('/buildings/edit/%i' % building.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        building = mommy.make(Building)
        response = self.client.get('/buildings/delete/%i' % building.pk)
        self.assertEqual(response.status_code, 200)


class RoomTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_room_creation(self):
        room = mommy.make(Room)
        building = mommy.make(Building)
        room_in_building = mommy.make(Room, building=building)
        self.assertTrue(isinstance(room, Room))
        self.assertEqual(str(room), room.name)
        self.assertTrue(isinstance(room_in_building, Room))
        self.assertEqual(str(room_in_building), room_in_building.name + " (" + str(building) + ")")
        self.assertEqual(room.get_absolute_url(), reverse('room-detail', kwargs={'pk': room.pk}))
        self.assertEqual(room.get_edit_url(), reverse('room-edit', kwargs={'pk': room.pk}))

    def test_list_view(self):
        mommy.make(Room, _quantity=40)

        response = self.client.get('/rooms/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["room_list"]), 30)
        self.assertEqual(response.context["paginator"].num_pages, 2)

        response = self.client.get('/rooms/2')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        room = mommy.make(Room)
        response = self.client.get('/rooms/view/%i' % room.pk)
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/rooms/add')
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        room = mommy.make(Room)
        response = self.client.get('/rooms/edit/%i' % room.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        room = mommy.make(Room)
        response = self.client.get('/rooms/delete/%i' % room.pk)
        self.assertEqual(response.status_code, 200)


class ManufacturerTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_manufacturer_creation(self):
        manufacturer = mommy.make(Manufacturer)
        self.assertTrue(isinstance(manufacturer, Manufacturer))
        self.assertEqual(str(manufacturer), manufacturer.name)
        self.assertEqual(manufacturer.get_absolute_url(),
                         reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        self.assertEqual(manufacturer.get_edit_url(), reverse('manufacturer-edit', kwargs={'pk': manufacturer.pk}))

    def test_list_view(self):
        mommy.make(Manufacturer, _quantity=40)

        response = self.client.get('/manufacturers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["manufacturer_list"]), 30)
        self.assertEqual(response.context["paginator"].num_pages, 2)

        response = self.client.get('/manufacturers/page/2')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        manufacturer = mommy.make(Manufacturer)
        response = self.client.get('/manufacturers/view/%i' % manufacturer.pk)
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/manufacturers/add')
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        manufacturer = mommy.make(Manufacturer)
        response = self.client.get('/manufacturers/edit/%i' % manufacturer.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        manufacturer = mommy.make(Manufacturer)
        response = self.client.get('/manufacturers/delete/%i' % manufacturer.pk)
        self.assertEqual(response.status_code, 200)


class TemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_template_creation(self):
        template = mommy.make(Template)
        self.assertTrue(isinstance(template, Template))
        self.assertEqual(str(template), template.templatename)
        self.assertEqual(template.get_absolute_url(), reverse('device-list'))
        self.assertEqual(template.get_as_dict(), {
            'name': template.name,
            'description': template.description,
            'manufacturer': template.manufacturer,
            'devicetype': template.devicetype,
        })

    def test_list_view(self):
        mommy.make(Template, _quantity=40)

        response = self.client.get('/devices/templates/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["template_list"]), 30)
        self.assertEqual(response.context["paginator"].num_pages, 2)

        response = self.client.get('/devices/templates/2')
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/devices/templates/add')
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        template = mommy.make(Template)
        response = self.client.get('/devices/templates/%i/edit/' % template.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        template = mommy.make(Template)
        response = self.client.get('/devices/templates/%i/delete/' % template.pk)
        self.assertEqual(response.status_code, 200)


class NoteTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_note_creation(self):
        note = mommy.make(Note)
        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.get_absolute_url(), reverse('device-detail', kwargs={'pk': note.device.pk}))


class DeviceInformationTypeTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', 'test')
        self.client.login(username='test', password='test')

    def test_device_information_type_creation(self):
        information = mommy.make(DeviceInformationType)
        self.assertTrue(isinstance(information, DeviceInformationType))
        self.assertEqual(str(information), information.humanname)


class DeviceInformationTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', 'test')
        self.client.login(username='test', password='test')

    def test_device_information_creation(self):
        device_information = mommy.make(DeviceInformation)
        self.assertEqual(str(device_information), str(device_information.infotype) + ": " + device_information.information)


class PictureTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_picture_creation(self):
        device = mommy.make(Device)
        picture = mommy.make(Picture, device=device)
        self.assertTrue(isinstance(picture, Picture))
        self.assertEqual(picture.get_absolute_url(), reverse('device-detail', kwargs={'pk': picture.device.pk}))
