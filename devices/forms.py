from django import forms
from network.models import IpAddress
from devices.models import Device, Type, Room, Manufacturer

charmodifier = (
	('icontains','Contains'),
	('istartswith', 'Starts with'),
	('iendswith','Ends with'),
	('iexact','Exact')
	)

class IpAddressForm(forms.Form):
    ipaddresses = forms.ModelMultipleChoiceField(
    	IpAddress.objects.filter(device=None),
    	widget=forms.SelectMultiple(attrs={"style":"width:100%;"}))
    device = forms.ModelChoiceField(Device.objects.all())

class SearchForm(forms.Form):
	error_css_class = 'error'
	name= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search name"}), required=False)
	namemodifier=forms.ChoiceField(choices=charmodifier, widget=forms.Select(attrs={"class":"postfix"}))

	buildnumber= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search buildnumber"}), required=False)
	buildnumbermodifier=forms.ChoiceField(choices=charmodifier, widget=forms.Select(attrs={"class":"postfix"}), required=False)

	serialnumber= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search serialnumber"}), required=False)
	serialnumbermodifier=forms.ChoiceField(choices=charmodifier, widget=forms.Select(attrs={"class":"postfix"}), required=False)

	macaddress= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search MAC-Address"}), required=False)
	macaddressmodifier=forms.ChoiceField(choices=charmodifier, widget=forms.Select(attrs={"class":"postfix"}), required=False)

	devicetype = forms.ModelChoiceField(Type.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
	manufacturer = forms.ModelChoiceField(Manufacturer.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
	room = forms.ModelChoiceField(Room.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
	ipaddress=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search IP-Address"}), required=False)
	overdue=forms.ChoiceField(choices=(('b', 'both'),('y', 'Yes'),('n', 'No'),), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))

	available=forms.ChoiceField(choices=(('b', 'both'),('y', 'Available'),('n', 'Unavailable'),), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
	lender = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search Lender"}), required=False)

class LendForm(forms.Form):
	owner = forms.CharField()
	duedate = forms.DateField(required=False, input_formats=('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d %Y',
'%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
'%B %d, %Y', '%d %B %Y', '%d %B, %Y'))

class ViewForm(forms.Form):
	viewfilter = forms.ChoiceField(choices=(
		('active', 'Active Devices'),
		('all', 'All Devices'),
		('available', 'Available Devices'),
		('unavailable', 'Unavailable Devices'),
		('archived', 'Archived Devices')),
		widget=forms.Select(attrs={"style":"width:200px;margin-right:10px;", "class":"right"}))