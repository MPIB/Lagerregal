from django import forms
from django.core.exceptions import ValidationError

import pystache
from django_select2.forms import Select2MultipleWidget

from devices.forms import get_emailrecipientlist
from mail.models import PREVIEW_DATA
from mail.models import MailTemplate


class MailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["default_recipients"].choices = get_emailrecipientlist()

        edit_usage = None
        if kwargs.get('instance'):
            edit_usage = kwargs['instance'].usage
        used_keys = MailTemplate.objects.values_list('usage', flat=True)

        valid_choices = [('', '--------')]
        for key, label in MailTemplate.USAGE_CHOICES:
            if key == edit_usage or key not in used_keys:
                valid_choices.append((key, label))
        self.fields["usage"].choices = valid_choices

    error_css_class = 'has-error'
    body = forms.CharField(widget=forms.Textarea())
    default_recipients = forms.MultipleChoiceField(required=False,
                                                   widget=Select2MultipleWidget())

    class Meta:
        model = MailTemplate
        fields = "__all__"

    def clean_body(self):
        body = self.cleaned_data['body']
        try:
            renderer = pystache.Renderer(missing_tags='strict')
            renderer.render(body, PREVIEW_DATA)
        except Exception as ex:
            raise ValidationError(str(ex), code='invalid') from ex
        return body
