# -*- coding: utf-8 -*-
from django import forms

from mail.models import MailTemplate
from devices.forms import get_emailrecipientlist


class MailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        self.fields["default_recipients"].choices = get_emailrecipientlist()

        if self.initial['mode'] == 'create':
            if self.initial['department']:
                used = MailTemplate.objects.values_list('usage', flat=True).filter(department = self.initial['department'])
                valid = [x for x in self.fields['usage'].choices if not any(y in x for y in used)]
                self.fields['usage'].choices = valid
                
        elif self.initial['mode'] == 'update':
            if self.instance.department:
                used = MailTemplate.objects.values_list('usage', flat=True).filter(department = kwargs["instance"].department)
                used = [x for x in used if str(self.instance.usage) not in x]
                valid = [x for x in self.fields['usage'].choices if not any(y in x for y in used)]
                self.fields['usage'].choices = valid

    error_css_class = 'has-error'
    body = forms.CharField(widget=forms.Textarea())
    default_recipients = forms.MultipleChoiceField(required=False)

    class Meta:
        model = MailTemplate
        fields= "__all__"
