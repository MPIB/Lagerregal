# -*- coding: utf-8 -*-
from django import forms

from mail.models import MailTemplate
from devices.forms import get_emailrecipientlist
import pdb

class MailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # self.request = kwargs.pop('request', None
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        # print "FORM CHOICES"
        # print self.fields['usage'].choices
        # print self.request
        self.fields["default_recipients"].choices = get_emailrecipientlist()
        # print("INITIAL!!!!!!")
        # print(self.initial)
        # print("INSTANCE")
        # print self.instance
        # print "FIELD!!!!"
        # print self.fields['department'].value()
        # self['usage'].valid()
        # if self.initial['mode'] == 'create':
        # if self.initial['department']:
        #     used = MailTemplate.objects.values_list('usage', flat=True).filter(department = self.initial['department'])
        #     valid = [x for x in self.fields['usage'].choices if not any(y in x for y in used)]
        #     self.fields['usage'].choices = valid
        #     print "FORM CHOICES INITIAL"
        #     print self.fields['usage'].choices


        # elif self.instance.department:
        #     used = MailTemplate.objects.values_list('usage', flat=True).filter(department = kwargs["instance"].department)
        #     used = [x for x in used if str(self.instance.usage) not in x]
        #     valid = [x for x in self.fields['usage'].choices if not any(y in x for y in used)]
        #     self.fields['usage'].choices = valid
        #     print "FORM CHOICES INSTANCE"
        #     print self.fields['usage'].choices

    # def is_valid(self):
    #     valid = super(MailTemplateForm, self).is_valid()
    #     pdb.set_trace()
    #     return valid
    #
    # def clean(self):
    #     cleaned_data = super(MailTemplateForm, self).clean()
    #     #pdb.set_trace()
    #     return cleaned_data

    error_css_class = 'has-error'
    body = forms.CharField(widget=forms.Textarea())
    default_recipients = forms.MultipleChoiceField(required=False)



    class Meta:
        model = MailTemplate
        fields= "__all__"

class MailTemplateUpdateForm(MailTemplateForm):
    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        print(kwargs)
        print self.initial
        print self.instance
        if self.instance.department:
            used = MailTemplate.objects.values_list('usage', flat=True).filter(department = kwargs["instance"].department)
            used = [x for x in used if str(self.instance.usage) not in x]
            valid = [x for x in self.fields['usage'].choices if not any(y in x for y in used)]
            self.fields['usage'].choices = valid
            print "FORM CHOICES INSTANCE"
            print self.fields['usage'].choices
        # if self.initial['department']:
        #     used = MailTemplate.objects.values_list('usage', flat=True).filter(department = self.initial['department'])
        #     valid = [x for x in self.fields['usage'].choices if not any(y in x for y in used)]
        #     self.fields['usage'].choices = valid
