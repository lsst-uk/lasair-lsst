from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from crispy_forms.helper import FormHelper
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.conf import settings
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3())
    email = forms.EmailField()
    privacy = forms.BooleanField(required=True)
    if getattr(settings, "DEBUG", False) and getattr(settings, "LASAIR_URL", False) == "127.0.0.1":
        captcha.clean = lambda x: True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'captcha', 'privacy']

    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            msg = 'A user with that email already exists.'
            self.add_error('email', msg)

        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            msg = 'This username is already taken, please try a different one.'
            self.add_error('username', msg)

        return self.cleaned_data


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image']

    def clean(self):
        image = self.cleaned_data.get('image')

        return self.cleaned_data
