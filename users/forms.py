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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'  # rôle client par défaut
        user.is_active = False  # compte inactif jusqu'à activation email
        if commit:
            user.save()
        return user

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


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nom_complet', 'username', 'email', 'contact', 'adresse', 'image']
        widgets = {
            'nom_complet': forms.TextInput(attrs={
                "class": "form-control form-control-lg rounded-pill shadow-sm",
                "placeholder": "Nom complet"
            }),
            'username': forms.TextInput(attrs={
                "class": "form-control form-control-lg rounded-pill shadow-sm",
                "placeholder": "Nom d'utilisateur"
            }),
            'email': forms.EmailInput(attrs={
                "class": "form-control form-control-lg rounded-pill shadow-sm",
                "placeholder": "Email"
            }),
            'contact': forms.TextInput(attrs={
                "class": "form-control form-control-lg rounded-pill shadow-sm",
                "placeholder": "Numéro de contact"
            }),
            'adresse': forms.TextInput(attrs={
                "class": "form-control form-control-lg rounded-pill shadow-sm",
                "placeholder": "Adresse"
            }),
            'image': forms.ClearableFileInput(attrs={
                "class": "form-control form-control-lg rounded-pill shadow-sm"
            }),
        }

