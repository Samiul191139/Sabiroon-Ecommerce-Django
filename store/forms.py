from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CreateUserForm(UserCreationForm):
    firstname = forms.CharField(max_length=30, required=True)
    lastname = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'firstname', 'lastname', 'email', 'password1', 'password2']
