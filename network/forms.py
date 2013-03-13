from django import forms

class AssignForm(forms.Form):
    ipaddress = forms.ModelChoiceField

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass