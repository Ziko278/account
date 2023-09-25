from django.forms import ModelForm, Select, TextInput, CheckboxInput, CheckboxSelectMultiple
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from account.models import *


class UserProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = UserProfileModel
        fields = '__all__'


class EmailForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = EmailModel
        fields = '__all__'


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

    class Meta:

        widgets = {
             'password': TextInput(attrs={
                 'class': 'form-control',
                 'type': 'password',
             }),

        }

