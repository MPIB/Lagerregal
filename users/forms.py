from django import forms
from django.utils.translation import ugettext_lazy as _
from users.models import Lageruser

class SettingsForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = Lageruser
        fields = ["pagelength", "timezone"]
        help_texts = {
            "pagelength" : _("The number of items displayed on one page in a list."),
        }

class AvatarForm(forms.ModelForm):
    error_css_class = 'has-error'
    avatar_clear = forms.BooleanField(required=False)
    class Meta:
        model = Lageruser
        fields = ["avatar"]
        widgets = {
            "avatar" : forms.FileInput()
        }