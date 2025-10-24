from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Service, ServiceImage
from tinymce.widgets import TinyMCE

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
            'description': TinyMCE(attrs={"rows": 20}),
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
            'ordre': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['ordre'].required = False

class BaseServiceImageFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['image'].required = False
            form.fields['ordre'].required = False
            form.empty_permitted = True

ServiceImageFormSet = inlineformset_factory(
    Service,
    ServiceImage,
    form=ServiceImageForm,
    formset=BaseServiceImageFormSet,
    extra=1,
    can_delete=True
)