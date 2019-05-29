from django import forms
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from Lagerregal import settings
from users.models import DepartmentUser
from users.models import Lageruser


class SettingsForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = Lageruser
        fields = ["pagelength", "timezone", "theme", "main_department"]
        help_texts = {
            "pagelength": _("The number of items displayed on one page in a list."),
            "main_department": _("Your Main department determines, which department devices you create are assigned to."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["timezone"].choices[0] = ("", ugettext("Default ({0})".format(settings.TIME_ZONE)))
        self.fields["timezone"].widget.choices[0] = ("", ugettext("Default ({0})".format(settings.TIME_ZONE)))


class AvatarForm(forms.ModelForm):
    error_css_class = 'has-error'
    avatar_clear = forms.BooleanField(required=False)

    class Meta:
        model = Lageruser
        fields = ["avatar"]
        widgets = {
            "avatar": forms.FileInput()
        }


class DepartmentAddUserForm(forms.ModelForm):
    error_css_class = 'has-error'

    class Meta:
        model = DepartmentUser
        widgets = {
            "department": forms.HiddenInput()
        }
        fields = '__all__'
