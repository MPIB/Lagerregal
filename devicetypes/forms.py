from django import forms
from django.forms.formsets import formset_factory
from devicetypes.models import Type

class TypeForm(forms.ModelForm):
    error_css_class = 'error'
    extra_fieldcount = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model=Type

    def __init__(self, *args, **kwargs):
        if "data" in kwargs:
            extra_fields = kwargs["data"]['extra_fieldcount']
        else:
            extra_fields = 1
        super(TypeForm, self).__init__(*args, **kwargs)
        self.fields['extra_fieldcount'].initial = extra_fields
        print extra_fields
        for index in range(int(extra_fields)):
            # generate extra fields in the number specified via extra_fields
            self.fields['extra_field_{index}'.format(index=index)] = \
                forms.CharField(label="Extra Attribute", widget=forms.TextInput(attrs={"class":"extra_attribute"}), required=False)

