from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg rounded-pill shadow-sm",
            "placeholder": "Nom d'utilisateur"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control form-control-lg rounded-pill shadow-sm",
            "placeholder": "Email"
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg rounded-pill shadow-sm",
            "placeholder": "Mot de passe"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg rounded-pill shadow-sm",
            "placeholder": "Confirmer le mot de passe"
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg rounded-pill shadow-sm",
            "placeholder": "Nom d'utilisateur ou email"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg rounded-pill shadow-sm",
            "placeholder": "Mot de passe"
        })
    )
