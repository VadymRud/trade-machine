from captcha.fields import CaptchaField
from django.contrib.auth import authenticate
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token

from clients.models import Client
from django import forms
from django.utils.translation import ugettext_lazy as _


class NewUserForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()

    class Meta:
        model = Client
        fields = ('email', 'first_name', 'last_name',)

    def clean(self):
        cleaned_data = super(NewUserForm, self).clean()

        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("password_confirm")

        if password1 != password2:
            self.add_error('password_confirm', _('Passwords must be identical'))
            return

        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(NewUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    token = None

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        # it is horrible, but its only for testing
        username = cleaned_data['email']
        password = cleaned_data['password']

        if username is None or password is None:
            return

        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            self.token = token

            return cleaned_data
        else:
            self.add_error('email', _('Account not found'))
            return
