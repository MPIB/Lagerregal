from django import forms
from django.utils.translation import ugettext_lazy as _


class SettingsForm(forms.Form):
    error_css_class = 'has-error'
    pagelength = forms.IntegerField(required=False, help_text=_("The number of items displayed on one page in a list."))

