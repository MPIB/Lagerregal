from django import forms
from devicetags.models import Devicetag
from devices.models import Device


class TagForm(forms.ModelForm):
    class Meta:
        model = Devicetag
        exclude = ["devices"]

class DeviceTagForm(forms.Form):
    error_css_class = 'has-error'
    tags = forms.ModelMultipleChoiceField(
        Devicetag.objects.all(),
        widget=forms.SelectMultiple(attrs={"style":"width:100%;"}))
    device = forms.ModelChoiceField(Device.objects.all())
