from django import forms
from network.models import IpAddress
from devices.models import Device, Type, Room, Manufacturer

class IpAddressForm(forms.Form):
    ipaddresses = forms.ModelMultipleChoiceField(
    	IpAddress.objects.filter(device=None),
    	widget=forms.SelectMultiple(attrs={"style":"width:100%;"}))
    device = forms.ModelChoiceField(Device.objects.all())

class SearchForm(forms.Form):
	name= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search name"}), required=False)
	devicetype = forms.ModelChoiceField(Type.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
	manufacturer = forms.ModelChoiceField(Manufacturer.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
	room = forms.ModelChoiceField(Room.objects.all(), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))
	ipaddress=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Search IP-Address"}), required=False)
	overdue=forms.ChoiceField(choices=(('b', 'both'),('y', 'Yes'),('n', 'No'),), required=False, widget=forms.Select(attrs={"style":"width:100%;"}))