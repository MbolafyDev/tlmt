from django import forms
from carousel.models import Slide

class SlideForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = ['titre', 'sous_titre', 'description', 'image', 'actif']
        widgets = {
            # on laisse les classes à minima : le template ajoutera form-control/formats
            'titre': forms.TextInput(),
            'sous_titre': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 3}),
            'actif': forms.CheckboxInput(),  # ✅ widget switch-compatible
        }
        labels = {
            'actif': 'Activer le slide',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # coché par défaut si ajout
        if not self.instance.pk:
            self.fields['actif'].initial = True
