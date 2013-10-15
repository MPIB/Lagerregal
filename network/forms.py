from django import forms
from django.utils.translation import ugettext_lazy as _

VIEWFILTER = (
    ('all', _('All IP-Addresses')),
    ('free', _('Free IP-Addresses')),
    ('used', _('Used IP-Addresses'))
 )

class AssignForm(forms.Form):
    ipaddress = forms.ModelChoiceField

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass

class ViewForm(forms.Form):
    viewfilter = forms.ChoiceField(choices=VIEWFILTER,
        widget=forms.Select(attrs={"style":"width:200px;margin-left:10px;", "class":"pull-right input-sm form-control"}))