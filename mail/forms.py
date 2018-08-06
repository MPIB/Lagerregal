# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
import six

from mail.models import USAGES
from mail.models import MailTemplate
from devices.forms import get_emailrecipientlist


class MailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        self.fields["default_recipients"].choices = get_emailrecipientlist()
        # templates that are already used
        used = MailTemplate.objects.values_list('usage', flat=True)
        # templates that are not used
        valid = [(str(x), six.text_type(y)) for x, y in USAGES if not any(z in x for z in used)]
        # if edit: append usage of edited template to valid choices
        if kwargs["instance"]:
            valid.append((kwargs["instance"].usage, [x[1] for x in USAGES if x[0] == kwargs["instance"].usage][0]))
        valid.insert(0, ('', '--------'))
        self.fields["usage"].choices = valid

    error_css_class = 'has-error'
    body = forms.CharField(widget=forms.Textarea())
    default_recipients = forms.MultipleChoiceField(required=False)

    class Meta:
        model = MailTemplate
        fields = "__all__"
