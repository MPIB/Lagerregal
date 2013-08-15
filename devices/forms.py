from django import forms
from network.models import IpAddress
from devices.models import Device, Type, Room, Manufacturer
from devicetypes.models import TypeAttribute, TypeAttributeValue
from users.models import Lageruser
import re
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

CHARMODIFIER = (
    ('icontains','Contains'),
    ('istartswith', 'Starts with'),
    ('iendswith','Ends with'),
    ('iexact','Exact')
    )

VIEWFILTER = (
    ('active', 'Active Devices'),
    ('all', 'All Devices'),
    ('available', 'Available Devices'),
    ('unavailable', 'Unavailable Devices'),
    ('archived', 'Archived Devices'))

class IpAddressForm(forms.Form):
    ipaddresses = forms.ModelMultipleChoiceField(
        IpAddress.objects.filter(device=None),
        widget=forms.SelectMultiple(attrs={"style":"width:100%;"}))
    device = forms.ModelChoiceField(Device.objects.all())

class SearchForm(forms.Form):
    error_css_class = 'error'
    searchname = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search name"}), required=False)
    namemodifier =forms.ChoiceField(choices=CHARMODIFIER, widget=forms.Select(attrs={"class":"postfix"}))

    bildnumber = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search buildnumber"}), required=False)
    bildnumbermodifier = forms.ChoiceField(choices=CHARMODIFIER, widget=forms.Select(attrs={"class":"postfix"}), required=False)

    serialnumber = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search serialnumber"}), required=False)
    serialnumbermodifier = forms.ChoiceField(choices=CHARMODIFIER, widget=forms.Select(attrs={"class":"postfix"}), required=False)

    macaddress = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search MAC-Address"}), required=False)
    macaddressmodifier = forms.ChoiceField(choices=CHARMODIFIER, widget=forms.Select(attrs={"class":"postfix"}), required=False)

    devicetype = forms.ModelChoiceField(Type.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
    manufacturer = forms.ModelChoiceField(Manufacturer.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
    room = forms.ModelChoiceField(Room.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
    ipaddress = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search IP-Address"}), required=False)
    overdue = forms.ChoiceField(choices=(('b', 'both'),('y', 'Yes'),('n', 'No'),), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))

    viewfilter = forms.ChoiceField(choices=VIEWFILTER, required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
    lender = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search Lender"}), required=False)

class LendForm(forms.Form):
    owner = forms.ModelChoiceField(Lageruser.objects.all(), widget=forms.Select(attrs={"style":"width:100%;"}))
    duedate = forms.DateField(required=False, input_formats=('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d %Y',
'%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
'%B %d, %Y', '%d %B %Y', '%d %B, %Y'))
    room = forms.ModelChoiceField(Room.objects.all(), required=False)

class ViewForm(forms.Form):
    viewfilter = forms.ChoiceField(choices=VIEWFILTER,
        widget=forms.Select(attrs={"style":"width:200px;margin-left:10px;", "class":"right"}))

class DeviceForm(forms.ModelForm):
    error_css_class = 'error'
    emailbosses = forms.BooleanField(required=False)
    emailmanagment = forms.BooleanField(required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'style':"height:80px"}), max_length=1000, required=False)
    webinterface = forms.URLField(max_length=60, required=False)
    creator =  forms.ModelChoiceField(queryset=Lageruser.objects.all(), widget=forms.HiddenInput())
    comment = forms.CharField(required=False)
    devicetype = forms.ModelChoiceField(Type.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
    manufacturer = forms.ModelChoiceField(Manufacturer.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
    room = forms.ModelChoiceField(Room.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
    class Meta:
        model=Device
        exclude = ("archived", "currentlending")

    def clean(self):
        cleaned_data = super(DeviceForm, self).clean()
        unclean_data = []
        for key, attribute in cleaned_data.iteritems():
                if key.startswith("attribute_") and attribute != "":
                    attributenumber = key.split("_")[1]
                    typeattribute = get_object_or_404(TypeAttribute, pk=attributenumber)
                    if re.match(typeattribute.regex, attribute) == None:
                        self._errors[key] = self.error_class([_("Doesn't match the given regex \"{0}\".".format(typeattribute.regex))])
                        unclean_data.append(key)
        for i in unclean_data:
            del cleaned_data[i]
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        if self.data != {}:
            try:
                attributes= TypeAttribute.objects.filter(devicetype = self.data["devicetype"][0])
            except:
                return
        elif kwargs["instance"] != None:
            print kwargs["instance"].pk
            attributevalues = TypeAttributeValue.objects.filter(device=kwargs["instance"].pk)
            if kwargs["instance"].devicetype != None:
                attributes= TypeAttribute.objects.filter(devicetype = kwargs["instance"].devicetype.pk)
            else:
                return
        else:
            attributes = []
        for attribute in attributes:
            # generate extra fields in the number specified via extra_fields
            self.fields['attribute_{index}'.format(index=attribute.pk)] = \
                forms.CharField(label=attribute.name, widget=forms.TextInput(attrs={"class":"extra_attribute"}), required=False)
            if 'attribute_{index}'.format(index=attribute.pk) in self.data:
                self.fields['attribute_{index}'.format(index=attribute.pk)].initial = self.data['attribute_{index}'.format(index=attribute.pk)]
            else:
                try:
                    self.fields['attribute_{index}'.format(index=attribute.pk)].initial = attributevalues.get(typeattribute=attribute.pk)
                except:
                    pass
            self.fields.keyOrder.insert(self.fields.keyOrder.index("room"), self.fields.keyOrder.pop(self.fields.keyOrder.index('attribute_{index}'.format(index=attribute.pk))))


class AddForm(forms.Form):
    name = forms.CharField(max_length=200)
    newclass = forms.ChoiceField(choices=[("manufacturer", "manufacturer"), ("devicetype", "devicetype"), ("room", "room")])