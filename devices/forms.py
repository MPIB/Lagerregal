from __future__ import unicode_literals
import re

from django import forms
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db.utils import OperationalError

from network.models import IpAddress
from devices.models import Device, Type, Room, Manufacturer
from devicetypes.models import TypeAttribute, TypeAttributeValue
from devicegroups.models import Devicegroup
from users.models import Lageruser, Department
from mail.models import MailTemplate


CHARMODIFIER = (
    ('icontains', _('Contains')),
    ('istartswith', _('Starts with')),
    ('iendswith', _('Ends with')),
    ('iexact', _('Exact'))
)

VIEWFILTER = (
    ('active', _('Active Devices')),
    ('all', _('All Devices')),
    ('available', _('Available Devices')),
    ('lent', _('Lent Devices')),
    ('archived', _('Archived Devices')),
    ('trashed', _('Trashed Devices')),
    ('overdue', _('Overdue Devices')),
    ('returnsoon', _('Return soon Devices')),
    ('temporary', _('Short term Devices')),
    ('bookmark', _('Bookmarked Devices'))
)

VIEWSORTING_DEVICES = (
    ('name', _('Name ascending')),
    ('-name', _('Name descending')),
    ('created_at', _('Age ascending')),
    ('-created_at', _('Age descending')),
    ('inventorynumber', _('Inventorynumber ascending')),
    ('-inventorynumber', _('Inventorynumber descending')),
    ('devicetype__name', _('Devicetype ascending')),
    ('-devicetype__name', _('Devicetype descending')),
    ('room__name', _('Room ascending')),
    ('-room__name', _('Room descending')),
    ('group__name', _('Devicegroup ascending')),
    ('-group__name', _('Devicegroup descending')),
    ('currentlending', _('Availability')),
)

VIEWSORTING = (
    ('name', _('Name ascending')),
    ('-name', _('Name descending')),
    ('id', _('ID ascending')),
    ('-id', _('ID descending')),
)

DEPARTMENT_OPTIONS = [
    ("all", _("All Departments")),
    ("my", _("My Departments"))
]


def get_department_options():
    try:
        return DEPARTMENT_OPTIONS+list(Department.objects.all().values_list("id", "name"))
    except OperationalError:
        return []


def get_devicegroup_options():
    try:
        return [('all', _('All Groups')), ]+list(Devicegroup.objects.all().values_list("id", "name"))
    except OperationalError:
        return []


def get_emailrecipientlist(special=None):
    objects = []

    if special:
        objects.append((_("Special"),
                        [(value, key) for key, value in special.iteritems()]
        ))

    objects.append((_("Groups"),
                    [("g" + str(group.id), group.name) for group in Group.objects.all().order_by("name")],
    ))
    objects.append((_("People"),
                    [("u" + str(user.id), user) for user in Lageruser.objects.all().order_by("last_name")],
    ))
    return objects


class IpAddressForm(forms.Form):
    error_css_class = 'has-error'
    ipaddresses = forms.ModelMultipleChoiceField(
        IpAddress.objects.filter(device=None, user=None),
        widget=forms.SelectMultiple(attrs={"style": "width:100%;"}))
    device = forms.ModelChoiceField(Device.objects.all())


class IpAddressPurposeForm(forms.Form):
    error_css_class = 'has-error'
    purpose = forms.CharField(required=False)


class SearchForm(forms.Form):
    error_css_class = 'has-error'
    searchname = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Search name", "class": "form-control input-sm"}), required=False)
    namemodifier = forms.ChoiceField(choices=CHARMODIFIER,
                                     widget=forms.Select(attrs={"class": "form-control input-sm"}))

    inventorynumber = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Search inventorynumber", "class": "form-control input-sm"}),
        required=False)
    inventorynumbermodifier = forms.ChoiceField(choices=CHARMODIFIER,
                                                widget=forms.Select(attrs={"class": "form-control input-sm"}),
                                                required=False)

    serialnumber = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Search serialnumber", "class": "form-control input-sm"}),
        required=False)
    serialnumbermodifier = forms.ChoiceField(choices=CHARMODIFIER,
                                             widget=forms.Select(attrs={"class": "form-control input-sm"}),
                                             required=False)

    macaddress = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Search MAC-Address", "class": "form-control input-sm"}),
        required=False)
    macaddressmodifier = forms.ChoiceField(choices=CHARMODIFIER,
                                           widget=forms.Select(attrs={"class": "form-control input-sm"}),
                                           required=False)

    devicetype = forms.ModelMultipleChoiceField(Type.objects.all(), required=False,
                                                widget=forms.SelectMultiple(attrs={"style": "width:100%;"}))
    manufacturer = forms.ModelMultipleChoiceField(Manufacturer.objects.all(), required=False,
                                                  widget=forms.SelectMultiple(attrs={"style": "width:100%;"}))
    devicegroup = forms.ModelMultipleChoiceField(Devicegroup.objects.all(), required=False,
                                                 widget=forms.SelectMultiple(attrs={"style": "width:100%;"}))
    room = forms.ModelMultipleChoiceField(Room.objects.all(), required=False,
                                          widget=forms.SelectMultiple(attrs={"style": "width:100%;"}))
    ipaddress = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Search IP-Address", "class": "form-control input-sm"}),
        required=False)
    overdue = forms.ChoiceField(choices=(('b', 'both'), ('y', 'Yes'), ('n', 'No'),), required=False,
                                widget=forms.Select(attrs={"style": "width:100%;"}))

    viewfilter = forms.ChoiceField(choices=VIEWFILTER, required=False,
                                   widget=forms.Select(attrs={"style": "width:100%;"}))
    lender = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Search Lender", "class": "form-control input-sm"}),
        required=False)


class LendForm(forms.Form):
    error_css_class = 'has-error'
    owner = forms.ModelChoiceField(Lageruser.objects.all(), widget=forms.Select(attrs={"style": "width:100%;"}),
                                   label=_("Lent to"))
    device = forms.ModelChoiceField(Device.objects.all(), widget=forms.Select(attrs={"style": "width:100%;"}),
                                    label=_("Device"), required=False)
    smalldevice = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control input-sm"}), required=False)
    duedate = forms.DateField(required=False, input_formats=('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d %Y',
                                                             '%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
                                                             '%B %d, %Y', '%d %B %Y', '%d %B, %Y', '%d.%m.%Y',
                                                             '%d.%m.%y'),
                              widget=forms.TextInput(attrs={"class": "form-control input-sm"}))
    room = forms.ModelChoiceField(Room.objects.select_related("building").all(), required=False)

    def clean(self):
        cleaned_data = super(LendForm, self).clean()
        if "device" in cleaned_data and "smalldevice" in cleaned_data:
            if cleaned_data["device"] and cleaned_data["smalldevice"]:
                raise forms.ValidationError("can not set both device and smalldevice")
            elif not cleaned_data["device"] and not cleaned_data["smalldevice"]:
                raise forms.ValidationError("you have to either set device or smalldevice")
        return cleaned_data

    def clean_device(self):
        device = self.cleaned_data["device"]
        if device:
            if device.currentlending:
                raise forms.ValidationError("this device is already lend.")
        return device


class ReturnForm(forms.Form):
    error_css_class = 'has-error'
    room = forms.ModelChoiceField(Room.objects.select_related("building").all(), required=False)


class DeviceViewForm(forms.Form):
    viewfilter = forms.ChoiceField(choices=VIEWFILTER,
                                   widget=forms.Select(attrs={"style": "width:150px;margin-left:10px;",
                                                              "class": "pull-right form-control input-sm"}))
    viewsorting = forms.ChoiceField(choices=VIEWSORTING_DEVICES,
                                    widget=forms.Select(attrs={"style": "width:150px;margin-left:10px;",
                                                               "class": "pull-right form-control input-sm"}))
    departmentfilter = forms.ChoiceField(choices=get_department_options(),
                                    widget=forms.Select(attrs={"style": "width:150px;margin-left:10px;",
                                                               "class": "pull-right form-control input-sm"}))


class ViewForm(forms.Form):
    viewsorting = forms.ChoiceField(choices=VIEWSORTING,
                                    widget=forms.Select(attrs={"style": "width:150px;margin-left:10px;",
                                                               "class": "pull-right form-control input-sm"}))


class DepartmentViewForm(ViewForm):
    viewfilter = forms.ChoiceField(choices=VIEWFILTER,
                                   widget=forms.Select(attrs={"style": "width:200px;margin-left:10px;",
                                                              "class": "pull-right input-sm form-control"}))
    departmentfilter = forms.ChoiceField(choices=get_department_options(),
                                    widget=forms.Select(attrs={"style": "width:150px;margin-left:10px;",
                                                               "class": "pull-right form-control input-sm"}))

class FilterForm(forms.Form):
    filterstring = forms.CharField(max_length=100,
                                   widget=forms.TextInput(attrs={"style": "width:150px;margin-left:10px;",
                                                                 "class": "pull-right form-control input-sm",
                                                                 "placeholder": "Filter"}))


class DepartmentFilterForm(FilterForm):
    departmentfilter = forms.ChoiceField(choices=get_department_options(),
                                    widget=forms.Select(attrs={"style": "width:150px;margin-left:10px;",
                                                               "class": "pull-right form-control input-sm"}))

class DeviceGroupFilterForm(FilterForm):
    groupfilter = forms.ChoiceField(choices=get_devicegroup_options(),
                                         widget=forms.Select(attrs={"style": "width:150px;margin-left:10px;",
                                                                        "class": "pull-right form-control input-sm"}))

class DeviceForm(forms.ModelForm):
    error_css_class = 'has-error'
    uses = forms.MultipleChoiceField(choices = Device.objects.none(), required = False)
    emailrecipients = forms.MultipleChoiceField(required=False)
    emailtemplate = forms.ModelChoiceField(queryset=MailTemplate.objects.all(), required=False, label=_("Template"),
                                           widget=forms.Select(attrs={"style": "width:100%;"}))
    emailedit = forms.BooleanField(required=False, label=_("Edit template"))
    emailsubject = forms.CharField(required=False, label=_("Subject"))
    emailbody = forms.CharField(widget=forms.Textarea(), required=False, label=_("Body"))

    description = forms.CharField(widget=forms.Textarea(attrs={'style': "height:80px"}), max_length=1000,
                                  required=False)
    webinterface = forms.URLField(max_length=60, required=False)
    creator = forms.ModelChoiceField(queryset=Lageruser.objects.all(), widget=forms.HiddenInput())
    comment = forms.CharField(required=False)
    devicetype = forms.ModelChoiceField(Type.objects.all(), required=False,
                                        widget=forms.Select(attrs={"style": "width:100%;"}))
    manufacturer = forms.ModelChoiceField(Manufacturer.objects.all(), required=False,
                                          widget=forms.Select(attrs={"style": "width:100%;"}))
    room = forms.ModelChoiceField(Room.objects.select_related("building").all(), required=False,
                                  widget=forms.Select(attrs={"style": "width:100%;"}))


    class Meta:
        model = Device
        exclude = ("archived", "currentlending", "bookmarkers", "inventoried", "trashed")

    def clean(self):
        cleaned_data = super(DeviceForm, self).clean()
        unclean_data = []
        if cleaned_data["emailrecipients"] and not cleaned_data["emailtemplate"]:
            self._errors["emailtemplate"] = self.error_class(
                [_("You specified recipients, but didn't select a template")])
        for key, attribute in cleaned_data.iteritems():
            if key.startswith("attribute_") and attribute != "":
                attributenumber = key.split("_")[1]
                typeattribute = get_object_or_404(TypeAttribute, pk=attributenumber)
                if re.match(typeattribute.regex, attribute) == None:
                    self._errors[key] = self.error_class(
                        [_("Doesn't match the given regex \"{0}\".".format(typeattribute.regex))])
                    unclean_data.append(key)
        for i in unclean_data:
            del cleaned_data[i]
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)

        #if edit
        if kwargs["instance"]:
            CHOICES = [(x.id, u''.join((x.name, " [" , str(x.id), "]")))for x in Device.objects.filter( trashed = None).exclude(pk = kwargs["instance"].id)]
            self.fields['uses'].choices = CHOICES
            self.initial['uses'] = [x.id for x in Device.objects.filter(used_in = kwargs["instance"].id)]
            self.fields['used_in'].queryset = Device.objects.filter(trashed = None).exclude(pk = kwargs["instance"].id)

        #if create
        else:
            CHOICES = [(x.id, u''.join((x.name, " [" , str(x.id) , "]"))) for x in Device.objects.filter(used_in = None, trashed = None)]
            self.fields['uses'].choices = CHOICES
            self.fields['used_in'].queryset = Device.objects.filter(trashed = None)

        self.fields['used_in'].label_from_instance = lambda obj: "%s [%s]" % (obj.name, obj.id)

        self.fields["emailrecipients"].choices = get_emailrecipientlist()
        if self.data != {}:
            try:
                attributes = TypeAttribute.objects.filter(devicetype__pk=self.data["devicetype"])
            except:
                return

        elif kwargs["instance"] != None:
            attributevalues = TypeAttributeValue.objects.filter(device=kwargs["instance"].pk)
            if kwargs["instance"].devicetype != None:
                attributes = TypeAttribute.objects.filter(devicetype=kwargs["instance"].devicetype.pk)
            else:
                return

        elif kwargs["initial"] != None:
            if "devicetype" in kwargs["initial"]:
                attributes = TypeAttribute.objects.filter(devicetype=kwargs["initial"]["devicetype"].pk)
            else:
                return
            attributevalues = TypeAttributeValue.objects.filter(device=kwargs["initial"]["deviceid"])
        else:
            attributes = []
        for attribute in attributes:
            # generate extra fields in the number specified via extra_fields
            self.fields['attribute_{index}'.format(index=attribute.pk)] = \
                forms.CharField(label=attribute.name,
                                widget=forms.TextInput(attrs={"class": "extra_attribute form-control"}), required=False)
            if 'attribute_{index}'.format(index=attribute.pk) in self.data:
                self.fields['attribute_{index}'.format(index=attribute.pk)].initial = self.data[
                    'attribute_{index}'.format(index=attribute.pk)]
            else:
                try:
                    self.fields['attribute_{index}'.format(index=attribute.pk)].initial = attributevalues.get(
                        typeattribute=attribute.pk)
                except:
                    pass


class AddForm(forms.ModelForm):
    error_css_class = 'has-error'
    classname = forms.ChoiceField(
        choices=[("manufacturer", "manufacturer"), ("devicetype", "devicetype"), ("room", "room"), ("group", "group")],
        widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(AddForm, self).clean()
        if cleaned_data["classname"] == "manufacturer":
            count = Manufacturer.objects.filter(name=cleaned_data["name"]).count()
        elif cleaned_data["classname"] == "devicetype":
            count = Type.objects.filter(name=cleaned_data["name"]).count()
        elif cleaned_data["classname"] == "room":
            count = Room.objects.filter(name=cleaned_data["name"]).count()
        elif cleaned_data["classname"] == "group":
            count = Devicegroup.objects.filter(name=cleaned_data["name"]).count()
        if count != 0:
            raise forms.ValidationError("Object with that Name already exists.")
        return cleaned_data


class DeviceMailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DeviceMailForm, self).__init__(*args, **kwargs)
        self.fields["emailrecipients"].choices = get_emailrecipientlist()

    error_css_class = 'has-error'
    emailrecipients = forms.MultipleChoiceField()
    mailtemplate = forms.ModelChoiceField(MailTemplate.objects.all())
    emailsubject = forms.CharField(required=False, label=_("Subject"))
    emailbody = forms.CharField(widget=forms.Textarea(), required=False, label=_("Body"))


class DeviceStorageForm(forms.Form):
    error_css_class = 'has-error'
    send_mail = forms.BooleanField(required=False)
