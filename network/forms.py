from django import forms
from django.utils.translation import ugettext_lazy as _
from network.models import IpAddress

VIEWFILTER = (
    ('all', _('All IP-Addresses')),
    ('free', _('Free IP-Addresses')),
    ('used', _('Used IP-Addresses')),
    ('byuser', _('Owned by User'))
 )

class IpAddressForm(forms.ModelForm):

    class Meta:
        model = IpAddress

    def clean(self):
        cleaned_data = super(IpAddressForm, self).clean()
        if cleaned_data["device"] != None and cleaned_data["user"] != None:
            raise forms.ValidationError(_("IP-Address can not be owned by a user and a device at the same time."))
        return cleaned_data

class ViewForm(forms.Form):
    viewfilter = forms.ChoiceField(choices=VIEWFILTER,
        widget=forms.Select(attrs={"style":"width:200px;margin-left:10px;", "class":"pull-right input-sm form-control"}))
