from django import forms
from network.models import IpAddress
from devices.models import Device, Type, Room, Manufacturer
from django.contrib.auth.models import User

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

    buildnumber = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search buildnumber"}), required=False)
    buildnumbermodifier = forms.ChoiceField(choices=CHARMODIFIER, widget=forms.Select(attrs={"class":"postfix"}), required=False)

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
    owner = forms.ModelChoiceField(User.objects.all(), widget=forms.Select(attrs={"style":"width:100%;"}))
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

    class Meta:
        model=Device
        exclude = ("archived", "currentlending")