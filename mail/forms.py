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
        fields= "__all__"

class MailTemplateUpdateForm(MailTemplateForm):
    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        if self.instance.department:
            #a query set
            used_db = MailTemplate.objects.values_list('usage', flat=True).filter(department = kwargs["instance"].department)
            used = []
            for x in used_db:
                if x is not None:
                    #the current templates' usage can't be excluded although it is in the used_db queryset
                    if not self.instance.usage == x:
                        used.append(x)
            #all usages that are not in used
            valid = [x for x in self.fields['usage'].choices if not any(y in x for y in used)]
            self.fields['usage'].choices = valid
