from django import forms
from .models import Dimensionnement, DemandeDimensionnement

class DimensionnementForm(forms.ModelForm):
    class Meta:
        model = Dimensionnement
        fields = "__all__"

class DemandeDimensionnementForm(forms.ModelForm):
    class Meta:
        model = DemandeDimensionnement
        fields = "__all__"
