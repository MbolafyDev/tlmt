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


class Couleur(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    code_hex = models.CharField(max_length=7, blank=True, null=True, help_text="Ex: #FF0000")

    class Meta:
        verbose_name = "Couleur"
        verbose_name_plural = "Couleurs"

    def __str__(self):
        return self.nom


class Produit(models.Model):
    categorie = models.ForeignKey(
        Categorie, on_delete=models.CASCADE, related_name="produits"
    )
    nom = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    description_courte = models.TextField(blank=True, null=True)
    description_detaillee = models.TextField(blank=True, null=True)

    prix_original = models.DecimalField(max_digits=10, decimal_places=2)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    avis = models.PositiveIntegerField(default=0)

    # Nouveau : relations
    caracteristiques = models.ManyToManyField(Caracteristique, blank=True, related_name="produits")
    couleurs = models.ManyToManyField(Couleur, blank=True, related_name="produits")

    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_ajout"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    @property
    def reduction(self):
        if self.prix_original > 0:
            return int(100 - (self.prix * 100 / self.prix_original))
        return 0


class ProduitImage(models.Model):
    produit = models.ForeignKey(
        Produit, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="produits/")
    principale = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produit"

    def __str__(self):
        return f"Image de {self.produit.nom}"
