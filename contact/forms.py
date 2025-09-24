# home/forms.py
from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['nom', 'email', 'sujet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 5}),
        }
