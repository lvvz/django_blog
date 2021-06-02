from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm, PasswordResetForm, UsernameField)
from django.contrib.auth import models as auth_models, get_user_model
from django.forms.utils import ErrorList

from . import models as M


class UserRegisterForm(forms.Form):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Enter username'}))
    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(
        label=("Password"),
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        strip=False,
    )
    password_confirm = forms.CharField(
        label=("Repeat password"),
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password'}),
        strip=False,
    )
    first_name = forms.CharField(max_length=128, widget=forms.TextInput())
    last_name = forms.CharField(max_length=128, widget=forms.TextInput())
    gender = forms.ChoiceField(choices=M.BlogUser.gender_choices, widget=forms.Select())
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD'}))

    def clean_password_confirm(self):
        pass1 = self.cleaned_data.get('password')
        pass2 = self.cleaned_data.get('password_confirm')
        if not pass2 or not pass2:
            raise forms.ValidationError('Password is empty')
        if pass2 != pass2:
            raise forms.ValidationError('Passwords do not match')
        return pass2

    def clean_username(self):
        try:
            same_username = get_user_model().objects.get_by_natural_key(self.cleaned_data.get('username'))
            if same_username:
                raise forms.ValidationError('Username already in use')
        except get_user_model().DoesNotExist:
            pass
        return self.cleaned_data.get('username')


class CommentForm(forms.ModelForm):
    class Meta:
        model = M.Comment
        fields = ['text']
        widgets = {'text': forms.Textarea(attrs={'class': 'textarea w-100', 'cols': False, 'rows': False})}


class PostForm(forms.ModelForm):
    class Meta:
        model = M.BlogPost
        fields = ['title', 'content']
        widgets = {'content': forms.Textarea(attrs={'class': 'textarea w-100', 'style': 'min-height:200px', 'cols': False, 'rows': False}),
                   'title': forms.TextInput(attrs={'class': 'w-100 '})}
