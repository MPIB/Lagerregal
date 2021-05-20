from django import forms
from django.utils.translation import ugettext_lazy as _

from django_select2.forms import Select2MultipleWidget

from devices.forms import get_department_options
from network.models import IpAddress

CATEGORIES = (
    ('all', _('All IP-Addresses')),
    ('free', _('Free IP-Addresses')),
    ('used', _('Used IP-Addresses')),
    ('byuser', _('Owned by User')),
    ('bydevice', _('Used by Device'))
)


class IpAddressForm(forms.ModelForm):
    class Meta:
        model = IpAddress
        exclude = ("last_seen", )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["device"] is not None and cleaned_data["user"] is not None:
            raise forms.ValidationError(_("IP-Address can not be owned by a user and a device at the same time."))
        return cleaned_data


class ViewForm(forms.Form):
    category = forms.ChoiceField(
        choices=CATEGORIES,
        widget=forms.Select(attrs={"class": "form-control-sm form-control"}),
    )
    department = forms.ChoiceField(
        choices=get_department_options(),
        widget=forms.Select(attrs={"class": "form-control form-control-sm"}),
    )


class UserIpAddressForm(forms.Form):
    error_css_class = 'has-error'
    ipaddresses = forms.ModelMultipleChoiceField(
        IpAddress.objects.filter(device=None, user=None),
        widget=Select2MultipleWidget(attrs={"data-token-separators": '[",", " "]'}))
