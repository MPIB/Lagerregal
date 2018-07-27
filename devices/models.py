from __future__ import unicode_literals

import datetime

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.core.exceptions import ValidationError

import reversion
import six

from users.models import Lageruser
from devicetypes.models import Type, TypeAttributeValue
from devicegroups.models import Devicegroup
from locations.models import Section
from Lagerregal import utils
from users.models import Department


@reversion.register()
@six.python_2_unicode_compatible
class Building(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)
    street = models.CharField(_('Street'), max_length=100, blank=True)
    number = models.CharField(_('Number'), max_length=30, blank=True)
    zipcode = models.CharField(_('ZIP code'), max_length=5, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    state = models.CharField(_('State'), max_length=100, blank=True)
    country = models.CharField(_('Country'), max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Building')
        verbose_name_plural = _('Buildings')
        permissions = (
            ("read_building", _("Can read Building")),
        )

    def get_absolute_url(self):
        return reverse('building-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('building-edit', kwargs={'pk': self.pk})


@reversion.register()
@six.python_2_unicode_compatible
class Room(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    building = models.ForeignKey(Building, null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL, related_name="rooms", blank=True)

    def __str__(self):
        if self.building:
            return self.name + " (" + six.text_type(self.building) + ")"
        else:
            return self.name

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        permissions = (
            ("read_room", _("Can read Room")),
        )

    def get_absolute_url(self):
        return reverse('room-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('room-edit', kwargs={'pk': self.pk})


@reversion.register()
@six.python_2_unicode_compatible
class Manufacturer(models.Model):
    name = models.CharField(_('Manufacturer'), max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Manufacturer')
        verbose_name_plural = _('Manufacturers')
        permissions = (
            ("read_manufacturer", _("Can read Manufacturer")),
        )

    def get_absolute_url(self):
        return reverse('manufacturer-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('manufacturer-edit', kwargs={'pk': self.pk})


class Bookmark(models.Model):
    device = models.ForeignKey("Device", on_delete=models.CASCADE)
    user = models.ForeignKey(Lageruser, on_delete=models.CASCADE)


class Vendor(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    driver_url = models.CharField(_('Drivers'), max_length=1000, blank=True, null=True)
    support_url = models.CharField(_('Support'), max_length=1000, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('vendor-edit', kwargs={'pk': self.pk})

    def clean_driver_url(self):
        print("HEYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
        driver_url = self.cleaned_data["driver_url"]
        if driver_url:
            if "SEARCHTAG" not in driver_url:
                raise ValidationError(_('Please call the variable url part SEARCHTAG (.../manuals/SEARCHTAG/...)'))
        return driver_url

    def clean_support_url(self):
        support_url = self.cleaned_data["support_url"]
        if support_url:
            if "SEARCHTAG" not in support_url:
                self.add_error('Please call the variable url part SEARCHTAG (.../manuals/SEARCHTAG/...)')
        return support_url


@six.python_2_unicode_compatible
class Device(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    creator = models.ForeignKey(Lageruser, on_delete=models.SET_NULL, null=True)
    name = models.CharField(_('Name'), max_length=200)
    inventorynumber = models.CharField(_('Inventorynumber'), max_length=50, blank=True)
    serialnumber = models.CharField(_('Serialnumber'), max_length=50, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True, on_delete=models.SET_NULL)
    hostname = models.CharField(_('Hostname'), max_length=40, blank=True)
    description = models.CharField(_('Description'), max_length=10000, blank=True)
    devicetype = models.ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL)
    room = models.ForeignKey(Room, blank=True, null=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(Devicegroup, blank=True, null=True, related_name="devices", on_delete=models.SET_NULL)
    webinterface = models.CharField(_('Webinterface'), max_length=60, blank=True)

    templending = models.BooleanField(default=False, verbose_name=_("For short term lending"))
    currentlending = models.ForeignKey("Lending", related_name="currentdevice", null=True, blank=True,
                                       on_delete=models.SET_NULL)

    manual = models.FileField(upload_to=utils.get_file_location, null=True, blank=True)
    contact = models.ForeignKey(Lageruser, related_name="as_contact",
                                help_text=_("Person to contact about using this device"), blank=True,
                                null=True, on_delete=models.SET_NULL)

    archived = models.DateTimeField(null=True, blank=True)
    trashed = models.DateTimeField(null=True, blank=True)
    inventoried = models.DateTimeField(null=True, blank=True)
    bookmarkers = models.ManyToManyField(Lageruser, through=Bookmark, related_name="bookmarks", blank=True)

    department = models.ForeignKey(Department, null=True, blank=True, related_name="devices", on_delete=models.SET_NULL)
    is_private = models.BooleanField(default=False)
    used_in = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')
        permissions = (
            ("boss_mails", _("Emails for bosses")),
            ("managment_mails", _("Emails for managment")),
            ("support_mails", _("Emails for support")),
            ("read_device", _("Can read Device")),
            ("lend_device", _("Can lend Device")),
            ("read_puppetdetails", _("Read Puppet Details"))
        )

    def get_absolute_url(self):
        return reverse('device-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('device-edit', kwargs={'pk': self.pk})

    def get_as_dict(self):
        dict = {}
        dict["name"] = self.name
        dict["description"] = self.description
        dict["manufacturer"] = self.manufacturer
        dict["devicetype"] = self.devicetype
        dict["room"] = self.room
        return dict

    def is_overdue(self):
        if self.currentlending is None:
            return False
        if self.currentlending.duedate < datetime.date.today():
            return True
        return False

    @staticmethod
    def active():
        return Device.objects.filter(archived=None, trashed=None)

    @staticmethod
    def devices_for_departments(departments=[]):
        return Device.objects.filter(department__in=departments).exclude(
            ~Q(department__in=departments), is_private=True)


@six.python_2_unicode_compatible
class DeviceInformationType(models.Model):
    keyname = models.CharField(_('Name'), max_length=200)
    humanname = models.CharField(_('Human readable name'), max_length=200)

    def __str__(self):
        return self.humanname

    class Meta:
        verbose_name = _('Information Type')
        verbose_name_plural = _('Information Type')


@six.python_2_unicode_compatible
class DeviceInformation(models.Model):
    information = models.CharField(_('Information'), max_length=200)
    device = models.ForeignKey(Device, related_name="information", on_delete=models.CASCADE)
    infotype = models.ForeignKey(DeviceInformationType, on_delete=models.CASCADE)

    def __str__(self):
        return six.text_type(self.infotype) + ": " + self.information

    class Meta:
        verbose_name = _('Information')
        verbose_name_plural = _('Information')


reversion.register(Device, follow=["typeattributevalue_set", ], exclude=[
    "archived", "currentlending", "inventoried", "bookmarks", "trashed",
], ignore_duplicates=True)
reversion.register(TypeAttributeValue)


@reversion.register(ignore_duplicates=True)
class Lending(models.Model):
    owner = models.ForeignKey(Lageruser, verbose_name=_("Lent to"), on_delete=models.SET_NULL, null=True)
    lenddate = models.DateField(auto_now_add=True)
    duedate = models.DateField(blank=True, null=True)
    duedate_email = models.DateField(blank=True, null=True)
    returndate = models.DateField(blank=True, null=True)
    device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.CASCADE)
    smalldevice = models.CharField(_("Small Device"), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _('Lending')
        verbose_name_plural = _('Lendings')


@six.python_2_unicode_compatible
class Template(models.Model):
    templatename = models.CharField(_('Templatename'), max_length=200)
    name = models.CharField(_('Name'), max_length=200)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True, on_delete=models.CASCADE)
    description = models.CharField(_('Description'), max_length=1000, blank=True)
    devicetype = models.ForeignKey(Type, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.templatename

    class Meta:
        ordering = ['name']
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')
        permissions = (
            ("read_template", _("Can read Template")),
        )

    def get_absolute_url(self):
        return reverse('device-list')

    def get_as_dict(self):
        dict = {}
        dict["name"] = self.name
        dict["description"] = self.description
        dict["manufacturer"] = self.manufacturer
        dict["devicetype"] = self.devicetype
        return dict


class Note(models.Model):
    device = models.ForeignKey(Device, related_name="notes", on_delete=models.CASCADE)
    note = models.CharField(max_length=5000)
    creator = models.ForeignKey(Lageruser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def get_absolute_url(self):
        return reverse("device-detail", kwargs={'pk': self.device.pk})


class Picture(models.Model):
    device = models.ForeignKey(Device, related_name="pictures", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=utils.get_file_location)
    caption = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Picture")
        verbose_name_plural = _("Pictures")

    def get_absolute_url(self):
        return reverse("device-detail", kwargs={'pk': self.device.pk})
