from django import forms
from django.forms import inlineformset_factory
from .models import Service, ServiceImage

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'titre', 'description', 'lieu',
            'date_debut', 'date_fin', 'duree',
            'statut', 'is_active'
        ]
        labels = {
            'duree': 'Durée du travail',
        }
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du service'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du service'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2 semaines'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ServiceImageForm(forms.ModelForm):
    class Meta:
        model = ServiceImage
        fields = ['image', 'ordre']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


ServiceImageFormSet = inlineformset_factory(
    Service,
    ServiceImage,
    form=ServiceImageForm,
    extra=0,
    can_delete=True
)
