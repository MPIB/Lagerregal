from django import forms

from django_select2.forms import Select2MultipleWidget

from devices.forms import get_emailrecipientlist
from mail.models import USAGES
from mail.models import MailTemplate


class MailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["default_recipients"].choices = get_emailrecipientlist()
        # get all valid options for template usages
        available = dict(USAGES)
        used_keys = MailTemplate.objects.values_list('usage', flat=True)
        valid_keys = set(available.keys()) - set(used_keys)
        valid_choices = []
        for key in valid_keys:
            valid_choices.append((key, available[key]))
        # if edit: append usage of edited template to valid choices
        edit_usage = kwargs['instance']
        if edit_usage is not None and edit_usage.usage is not None:
            valid_choices.append((edit_usage.usage, available[edit_usage.usage]))
        valid_choices.insert(0, ('', '--------'))
        self.fields["usage"].choices = valid_choices

    error_css_class = 'has-error'
    body = forms.CharField(widget=forms.Textarea())
    default_recipients = forms.MultipleChoiceField(required=False,
                                                   widget=Select2MultipleWidget())

    class Meta:
        model = MailTemplate
        fields = "__all__"
