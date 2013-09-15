from django.db import models
from users.models import Lageruser
from devicetypes.models import Type, TypeAttributeValue
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import reversion


class Building(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)
    street = models.CharField(_('Street'), max_length = 100, blank = True)
    number = models.CharField(_('Number'), max_length = 30, blank = True)
    zipcode = models.CharField(_('ZIP code'), max_length = 5, blank = True)
    city = models.CharField(_('City'), max_length = 100, blank = True)
    state = models.CharField(_('State'), max_length = 100, blank = True)
    country = models.CharField(_('Country'), max_length = 100, blank = True)
    def __unicode__(self):
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


class Room(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)
    building = models.ForeignKey(Building, null=True)

    def __unicode__(self):
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

class Manufacturer(models.Model):
    name = models.CharField(_('Manufacturer'), max_length=200, unique=True)

    def __unicode__(self):
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

class Device(models.Model):
    created_at = models.DateTimeField(auto_now_add = True, blank=True, null=True)
    creator = models.ForeignKey(Lageruser)
    name = models.CharField(_('Name'), max_length=200)
    bildnumber = models.CharField(_('Bildnumber'), max_length=50)
    serialnumber = models.CharField(_('Serialnumber'), max_length=50)
    macaddress = models.CharField(_('MAC Address'), max_length=40)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True)
    hostname = models.CharField(_('Hostname'), max_length=40, blank=True)
    description = models.CharField(_('Description'), max_length=1000, blank=True)
    devicetype = models.ForeignKey(Type, blank=True, null=True)
    room = models.ForeignKey(Room, blank=True, null=True)
    webinterface = models.CharField(_('Webinterface'), max_length=60, blank=True)

    currentlending = models.ForeignKey("Lending", related_name="currentdevice", null=True, blank=True)

    archived = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')
        permissions = (
            ("boss_mails", _("Emails for bosses")),
            ("managment_mails", _("Emails for managment")),
            ("support_mails", _("Emails for support")),
            ("read_device", _("Can read Device")),
            ("lend_device", _("Can lend Device"))
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

reversion.register(Device, follow=["typeattributevalue_set"], exclude=["archived", "currentlending"])
reversion.register(TypeAttributeValue)


class Lending(models.Model):
    owner = models.ForeignKey(Lageruser)
    lenddate = models.DateField(auto_now_add=True)
    duedate = models.DateField(blank=True, null=True)
    duedate_email = models.DateField(blank=True, null=True)
    returndate = models.DateField(blank=True, null=True)
    device = models.ForeignKey(Device)

class Template(models.Model):
    templatename = models.CharField(_('Templatename'), max_length=200)
    name = models.CharField(_('Name'), max_length=200)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True)
    description = models.CharField(_('Description'), max_length=1000, blank=True)
    devicetype = models.ForeignKey(Type, blank=True, null=True)

    def __unicode__(self):
        return self.templatename

    class Meta:
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