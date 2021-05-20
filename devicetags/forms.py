from django import forms

from django_select2.forms import Select2MultipleWidget

from devicetags.models import Devicetag


class TagForm(forms.ModelForm):
    class Meta:
        model = Devicetag
        exclude = ["devices"]


class DeviceTagForm(forms.Form):
    error_css_class = 'has-error'
    tags = forms.ModelMultipleChoiceField(
        Devicetag.objects.all(),
        widget=Select2MultipleWidget(attrs={"data-token-separators": '[",", " "]'}))
