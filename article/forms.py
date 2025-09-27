from django import forms
from article.models import Produit, Categorie, Caracteristique

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            "categorie",
            "nom",
            "description_courte",
            "description_detaillee",
            "prix_original",
            "prix",
            "caracteristiques",
            # "couleurs",  # ← décommente si tu veux aussi gérer les couleurs
        ]
        labels = {
            "categorie": "Catégorie",
            "nom": "Nom du produit",
            "description_courte": "Description courte",
            "description_detaillee": "Description détaillée",
            "prix_original": "Prix d’origine",
            "prix": "Prix actuel",
            "caracteristiques": "Caractéristiques",
            # "couleurs": "Couleurs",
        }
        widgets = {
            "categorie": forms.Select(attrs={"class": "form-select"}),
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "description_courte": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "description_detaillee": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "prix_original": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "prix": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "caracteristiques": forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
            # "couleurs": forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
        }

    # (Facultatif) pour limiter les listes si besoin
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categorie"].queryset = Categorie.objects.order_by("nom")
        self.fields["caracteristiques"].queryset = Caracteristique.objects.order_by("nom")
