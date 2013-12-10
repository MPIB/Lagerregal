from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from users.models import Lageruser
from Lagerregal import settings

class SettingsForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = Lageruser
        fields = ["pagelength", "timezone"]
        help_texts = {
            "pagelength" : _("The number of items displayed on one page in a list."),
        }

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields["timezone"].choices[0] = ("", ugettext("Default ({0})".format(settings.TIME_ZONE)))
        self.fields["timezone"].widget.choices[0] = ("", ugettext("Default ({0})".format(settings.TIME_ZONE)))

class AvatarForm(forms.ModelForm):
    error_css_class = 'has-error'
    avatar_clear = forms.BooleanField(required=False)
    class Meta:
        model = Lageruser
        fields = ["avatar"]
        widgets = {
            "avatar" : forms.FileInput()
        }