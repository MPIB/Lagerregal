from __future__ import unicode_literals

from django import forms

from django_select2.forms import Select2MultipleWidget

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
        widget=Select2MultipleWidget(attrs={"style": "width:100%;", "data-token-separators": '[",", " "]'}))
    device = forms.ModelChoiceField(Device.objects.all())
