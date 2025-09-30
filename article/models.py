from django.db import models
from django.utils.text import slugify


def _unique_slug_for(model_cls, base_text, *, pk_to_exclude=None, fallback="item"):
    """
    Génère un slug unique pour model_cls à partir de base_text.
    Ajoute -2, -3, ... en cas de collision. Exclut pk_to_exclude (pour l'update).
    """
    base = slugify(base_text or "") or fallback
    candidate = base
    i = 2

    qs = model_cls.objects.all()
    if pk_to_exclude is not None:
        qs = qs.exclude(pk=pk_to_exclude)

    while qs.filter(slug=candidate).exists():
        candidate = f"{base}-{i}"
        i += 1
    return candidate


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        """
        Crée un slug unique si absent, ou si le nom a changé.
        """
        old_nom = None
        if self.pk:
            old_nom = type(self).objects.filter(pk=self.pk).values_list("nom", flat=True).first()

        if not self.slug or (old_nom is not None and old_nom != self.nom):
            self.slug = _unique_slug_for(type(self), self.nom, pk_to_exclude=self.pk, fallback="categorie")

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

    # Relations
    caracteristiques = models.ManyToManyField(Caracteristique, blank=True, related_name="produits")
    couleurs = models.ManyToManyField(Couleur, blank=True, related_name="produits")

    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_ajout"]

    def __str__(self):
        return self.nom

    @property
    def reduction(self):
        if self.prix_original and self.prix_original > 0:
            return int(100 - (self.prix * 100 / self.prix_original))
        return 0

    def save(self, *args, **kwargs):
        """
        Crée un slug unique si absent, ou si le nom a changé.
        """
        old_nom = None
        if self.pk:
            old_nom = type(self).objects.filter(pk=self.pk).values_list("nom", flat=True).first()

        if not self.slug or (old_nom is not None and old_nom != self.nom):
            self.slug = _unique_slug_for(type(self), self.nom, pk_to_exclude=self.pk, fallback="produit")

        super().save(*args, **kwargs)


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


