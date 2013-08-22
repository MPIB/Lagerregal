from django import forms
from django.utils.translation import ugettext_lazy as _


class AppearanceForm(forms.Form):
    pagelength = forms.IntegerField(required=False)

