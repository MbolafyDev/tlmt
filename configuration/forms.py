from django import forms
from users.models import CustomUser

class UserValidationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role', 'validated_by_admin', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'validated_by_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
