from django import forms
from users.models import CustomUser
from article.models import Produit, ProduitImage
from plomberie.models import AppareilSanitaire
from tinymce.widgets import TinyMCE

class UserValidationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role', 'validated_by_admin', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'validated_by_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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
            "couleurs",
        ]
        widgets = {
            'nom': forms.TextInput(attrs={"class": "form-control"}),
            "description_courte": TinyMCE(attrs={"rows": 20}),
            "description_detaillee": TinyMCE(attrs={"rows": 20}),
            'prix_original': forms.NumberInput(attrs={"class": "form-control"}),
            'prix': forms.NumberInput(attrs={"class": "form-control"}),
            'categorie': forms.Select(attrs={"class": "form-control"}),
            'caracteristiques': forms.SelectMultiple(attrs={"class": "form-control"}),
            'couleurs': forms.SelectMultiple(attrs={"class": "form-control"}),
        }
import json
from django.db import models
from django.utils.text import slugify


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Caracteristique(models.Model):
    nom = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Caractéristique"
        verbose_name_plural = "Caractéristiques"

    def __str__(self):
        return self.nom


class UserValidationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role', 'validated_by_admin', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'validated_by_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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
            "couleurs",
            "is_active",  # ← ajouté
        ]
        widgets = {
            'nom': forms.TextInput(attrs={"class": "form-control"}),
            "description_courte": TinyMCE(attrs={"rows": 20}),
            "description_detaillee": TinyMCE(attrs={"rows": 20}),
            'prix_original': forms.NumberInput(attrs={"class": "form-control"}),
            'prix': forms.NumberInput(attrs={"class": "form-control"}),
            'categorie': forms.Select(attrs={"class": "form-control"}),
            'caracteristiques': forms.SelectMultiple(attrs={"class": "form-control"}),
            'couleurs': forms.SelectMultiple(attrs={"class": "form-control"}),
            'is_active': forms.CheckboxInput(attrs={"class": "form-check-input"}),  # ← widget pour checkbox
        }

class ProduitImageForm(forms.ModelForm):
    class Meta:
        model = ProduitImage
        fields = ['image', 'principale']
        widgets = {
            'image': forms.ClearableFileInput(attrs={"class": "form-control"}),
            'principale': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class AppareilSanitaireForm(forms.ModelForm):
    class Meta:
        model = AppareilSanitaire
        fields = ["nom", "debit_brut", "eau_chaude", "image"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "debit_brut": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "eau_chaude": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }