from django import forms

VIEWFILTER = (
    ('all', 'All IP-Addresses'),
    ('free', 'Free IP-Addresses'),
    ('used', 'Used IP-Addresses')
 )

class AssignForm(forms.Form):
    ipaddress = forms.ModelChoiceField

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass

class ViewForm(forms.Form):
    viewfilter = forms.ChoiceField(choices=VIEWFILTER,
        widget=forms.Select(attrs={"style":"width:200px;margin-left:10px;", "class":"right"}))