from django import forms
from django.forms.formsets import formset_factory
from mail.models import MailTemplate

class MailTemplateForm(forms.ModelForm):
    error_css_class = 'has-error'
    body = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = MailTemplate
