# -*- coding: utf-8 -*-
from django import forms

from mail.models import MailTemplate
from devices.forms import get_emailrecipientlist


class MailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        self.fields["default_recipients"].choices = get_emailrecipientlist()

    error_css_class = 'has-error'
    body = forms.CharField(widget=forms.Textarea())
    default_recipients = forms.MultipleChoiceField(required=False)

    class Meta:
        model = MailTemplate
        fields = ("name", "subject", "body", "usage", "department")
