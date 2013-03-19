from django import forms
from network.models import IpAddress
from devices.models import Device

class IpAddressForm(forms.Form):
    ipaddresses = forms.ModelMultipleChoiceField(
    	IpAddress.objects.filter(device=None),
    	widget=forms.SelectMultiple(attrs={"style":"width:100%;"}))
    device = forms.ModelChoiceField(Device.objects.all())
