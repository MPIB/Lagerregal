import os.path

from datetime import datetime, timedelta

from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse
from model_mommy import mommy

from devices.models import Device, Building, Room, Manufacturer, Template, Note, Lending, DeviceInformationType, DeviceInformation, Picture
from users.models import Lageruser
from network.models import IpAddress
from devices.forms import IpAddressForm
from devices.forms import DeviceForm


class DeviceTests(TestCase):

    def setUp(self):
        '''method for setting up a client for testing'''
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_device_creation(self):
        '''method for testing the functionality of creating a new device'''
        device = mommy.make(Device)
        lending_past = mommy.make(Lending, duedate = (datetime.today() - timedelta(days = 1)).date())
        lending_future = mommy.make(Lending, duedate = (datetime.today() + timedelta(days = 1)).date())
        self.assertTrue(isinstance(device, Device))
        self.assertEqual(device.__str__(), device.name)
        self.assertEqual(device.get_absolute_url(), reverse('device-detail', kwargs={'pk': device.pk}))
        self.assertEqual(device.get_edit_url(), reverse('device-edit', kwargs={'pk': device.pk}))
        self.assertEqual(device.get_as_dict(), {"name": device.name, "description": device.description, "manufacturer": device.manufacturer, "devicetype" : device.devicetype, "room" : device.room})
        self.assertFalse(device.is_overdue())
        self.assertTrue(mommy.make(Device, currentlending = lending_past).is_overdue())
        self.assertFalse(mommy.make(Device, currentlending = lending_future).is_overdue())

    def test_device_list(self):
        devices = mommy.make(Device, _quantity=40)
        url = reverse("device-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["device_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("device-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_device_detail(self):
        device = mommy.make(Device)
        devices = Device.objects.all()
        device = devices[0]
        ip = IpAddress(address="127.0.0.1")
        ip.save()
        url = reverse("device-detail", kwargs={"pk": device.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_device_add(self):
        device = mommy.make(Device, name = "used")
        url = reverse("device-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        form = resp.context['form']
        data = form.initial
        data['uses'] = device.id
        data['name'] = "uses"
        resp = self.client.post(url, data)
        device = Device.objects.filter(name = 'used')[0]
        self.assertEqual(device.used_in.name, 'uses')

    def test_device_edit(self):
        device = mommy.make(Device)
        url = reverse("device-edit", kwargs={"pk": device.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_device_delete(self):
        device = mommy.make(Device)
        devices = Device.objects.all()
        device = devices[0]
        url = reverse("device-delete", kwargs={"pk": device.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_device_archive(self):
        device = mommy.make(Device)
        devices = Device.objects.all()
        device = devices[0]
        archiveurl = reverse("device-archive", kwargs={"pk": device.pk})
        resp = self.client.post(archiveurl)
        self.assertEqual(resp.status_code, 302)
        url = reverse("device-detail", kwargs={"pk": device.pk})
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
        devices = Device.objects.all()
        device = devices[0]
        trashurl = reverse("device-trash", kwargs={"pk": device.pk})
        resp = self.client.post(trashurl)
        self.assertEqual(resp.status_code, 302)
        url = reverse("device-detail", kwargs={"pk": device.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["device"].trashed)

        resp = self.client.post(trashurl)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.context["device"].trashed)

    def test_device_trash_sets_child_used_in_to_none(self):
        device = mommy.make(Device)
        used_device = mommy.make(Device, used_in = device)
        trashurl = reverse('device-trash', kwargs={'pk': device.pk})
        resp = self.client.post(trashurl)
        used_device = Device.objects.filter(pk = used_device.pk)[0]
        self.assertIsNone(used_device.used_in)

    def test_device_trash_sets_self_used_in_to_none(self):
        device = mommy.make(Device, _fill_optional=['used_in'])
        trashurl = reverse("device-trash", kwargs={'pk' : device.pk})
        resp = self.client.post(trashurl)
        device = Device.objects.filter(pk = device.pk)[0]
        self.assertIsNone(device.used_in)

    def test_device_trash_returns_lending(self):
        lending = mommy.make(Lending, _fill_optional=['device', 'owner'])
        lending.device.currentlending = lending
        lending.device.save()
        trashurl = reverse("device-trash", kwargs={"pk": lending.device.pk})
        resp = self.client.post(trashurl)
        lending.refresh_from_db()
        self.assertIsNotNone(lending.returndate)

    def test_device_inventoried(self):
        device = mommy.make(Device)
        devices = Device.objects.all()
        device = devices[0]
        url = reverse("device-inventoried", kwargs={"pk": device.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        url = reverse("device-detail", kwargs={"pk": device.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["device"].inventoried)

    def test_device_bookmark(self):
        device = mommy.make(Device)
        devices = Device.objects.all()
        device = devices[0]
        bookmarkurl = reverse("device-trash", kwargs={"pk": device.pk})
        url = reverse("device-detail", kwargs={"pk": device.pk})
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
        devices = Device.objects.all()
        device = devices[0]
        url = reverse("device-ipaddress", kwargs={"pk": device.pk})
        resp = self.client.post(url, {"ipaddresses": [ip.pk], "device": device.pk})
        self.assertEqual(resp.status_code, 302)
        deviceurl = reverse("device-detail", kwargs={"pk": device.pk})
        resp = self.client.get(deviceurl)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["device"].ipaddress_set.all()), 1)

        url = reverse("device-ipaddress-remove", kwargs={"pk": device.pk, "ipaddress": ip.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(deviceurl)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["device"].ipaddress_set.all()), 0)

    def test_device_lending_list(self):
        lending = mommy.make(Lending)
        device = mommy.make(Device, currentlending = lending)
        url = reverse("device-lending-list", kwargs = {"pk": device.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_device_lend(self):
        device = mommy.make(Device, archived = None)
        room = mommy.make(Room)
        room.save()
        lending = mommy.make(Lending)
        lending.save()
        devices = Device.objects.all()
        device = devices[0]
        url = reverse("device-lend")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        deviceurl = reverse("device-detail", kwargs={"pk": device.pk})
        resp = self.client.get(deviceurl)
        self.assertEqual(resp.status_code, 200)

    def test_device_return(self):
        device = mommy.make(Device)
        devices = Device.objects.all()
        device = devices[0]
        user = mommy.make(Lageruser)

        lending = mommy.make(Lending, owner = user)
        url = reverse("device-return", kwargs = {"lending": lending.id})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)

        lending2 = mommy.make(Lending, device = device)
        url = reverse("device-return", kwargs = {"lending": lending2.id})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)


class BuildingTests(TestCase):
    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_building_creation(self):
        building = mommy.make(Building)
        building.save()
        self.assertTrue(isinstance(building, Building))
        self.assertEqual(building.__str__(), building.name)
        self.assertEqual(building.get_absolute_url(), reverse('building-detail', kwargs={'pk': building.pk}))
        self.assertEqual(building.get_edit_url(), reverse('building-edit', kwargs={'pk': building.pk}))

    def test_building_list(self):
        buildings = mommy.make(Building, _quantity=40)
        url = reverse("building-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["building_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("building-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_building_detail(self):
        building = mommy.make(Building)
        buildings = Building.objects.all()
        building = buildings[0]
        url = reverse("building-detail", kwargs={"pk": building.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_building_add(self):
        building = mommy.make(Building)
        buildings = Building.objects.all()
        building = buildings[0]
        url = reverse("building-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_building_edit(self):
        building = mommy.make(Building)
        buildings = Building.objects.all()
        building = buildings[0]
        url = reverse("building-edit", kwargs={"pk": building.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_building_delete(self):
        building = mommy.make(Building)
        buildings = Building.objects.all()
        building = buildings[0]
        url = reverse("building-delete", kwargs={"pk": building.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class RoomTests(TestCase):
    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_room_creation(self):
        room = mommy.make(Room)
        building = mommy.make(Building)
        room_in_building = mommy.make(Room, building = building)
        self.assertTrue(isinstance(room, Room))
        self.assertEqual(room.__str__(), room.name)
        self.assertTrue(isinstance(room_in_building, Room))
        self.assertEqual(room_in_building.__str__(), room_in_building.name + " (" + building.__str__() + ")")
        self.assertEqual(room.get_absolute_url(), reverse('room-detail', kwargs={'pk': room.pk}))
        self.assertEqual(room.get_edit_url(), reverse('room-edit', kwargs={'pk': room.pk}))

    def test_room_list(self):
        rooms = mommy.make(Room, _quantity=40)
        url = reverse("room-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["room_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("room-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_room_detail(self):
        room = mommy.make(Room)
        rooms = Room.objects.all()
        room = rooms[0]
        url = reverse("room-detail", kwargs={"pk": room.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_room_add(self):
        room = mommy.make(Room)
        url = reverse("room-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_room_edit(self):
        room = mommy.make(Room)
        rooms = Room.objects.all()
        room = rooms[0]
        url = reverse("room-edit", kwargs={"pk": room.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_room_delete(self):
        room = mommy.make(Room)
        rooms = Room.objects.all()
        room = rooms[0]
        url = reverse("room-delete", kwargs={"pk": room.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class ManufacturerTests(TestCase):
    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_manufacturer_creation(self):
        manufacturer = mommy.make(Manufacturer)
        self.assertTrue(isinstance(manufacturer, Manufacturer))
        self.assertEqual(manufacturer.__str__(), manufacturer.name)
        self.assertEqual(manufacturer.get_absolute_url(),
                         reverse('manufacturer-detail', kwargs={'pk': manufacturer.pk}))
        self.assertEqual(manufacturer.get_edit_url(), reverse('manufacturer-edit', kwargs={'pk': manufacturer.pk}))

    def test_manufacturer_list(self):
        manufacturers = mommy.make(Manufacturer, _quantity=40)
        url = reverse("manufacturer-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["manufacturer_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("manufacturer-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_manufacturer_detail(self):
        manufacturer = mommy.make(Manufacturer)
        manufacturers = Manufacturer.objects.all()
        manufacturer = manufacturers[0]
        url = reverse("manufacturer-detail", kwargs={"pk": manufacturer.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_manufacturer_add(self):
        manufacturer = mommy.make(Manufacturer)
        url = reverse("manufacturer-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_manufacturer_edit(self):
        manufacturer = mommy.make(Manufacturer)
        manufacturers = Manufacturer.objects.all()
        manufacturer = manufacturers[0]
        url = reverse("manufacturer-edit", kwargs={"pk": manufacturer.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_manufacturer_delete(self):
        manufacturer = mommy.make(Manufacturer)
        manufacturers = Manufacturer.objects.all()
        manufacturer = manufacturers[0]
        url = reverse("manufacturer-delete", kwargs={"pk": manufacturer.pk})
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
        self.assertEqual(template.__str__(), template.templatename)
        self.assertEqual(template.get_absolute_url(), reverse('device-list'))
        self.assertEqual(template.get_as_dict(), {'name': template.name, 'description': template.description, 'manufacturer' : template.manufacturer, 'devicetype' : template.devicetype })

    def test_template_list(self):
        templates = mommy.make(Template, _quantity=40)
        url = reverse("template-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["template_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("template-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_template_add(self):
        template = mommy.make(Template)
        url = reverse("template-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_template_edit(self):
        template = mommy.make(Template)
        templates = Template.objects.all()
        template = templates[0]
        url = reverse("template-edit", kwargs={"pk": template.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_template_delete(self):
        template = mommy.make(Template)
        templates = Template.objects.all()
        template = templates[0]
        url = reverse("template-delete", kwargs={"pk": template.pk})
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

class DeviceInformationTypeTests(TestCase):
    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', 'test')
        self.client.login(username = 'test', password = 'test')

    def test_device_information_type_creation(self):
        information = mommy.make(DeviceInformationType)
        self.assertTrue(isinstance(information, DeviceInformationType))
        self.assertEqual(information.__str__(), information.humanname)

class DeviceInformationTests(TestCase):
    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', 'test')
        self.client.login(username = 'test', password = 'test')

    def test_device_information_creation(self):
        device_information = mommy.make(DeviceInformation)
        self.assertEqual(device_information.__str__(), device_information.infotype.__str__() + ": " + device_information.information)


class PictureTests(TestCase):
    def setUp(self):
        self.client = Client()
        my_admin = Lageruser.objects.create_superuser('test', 'test@test.com', "test")
        self.client.login(username="test", password="test")

    def test_picture_creation(self):
        device = mommy.make(Device)
        picture = mommy.make(Picture, device = device)
        self.assertTrue(isinstance(picture, Picture))
        self.assertEqual(picture.get_absolute_url(), reverse('device-detail', kwargs={'pk': picture.device.pk}) )
