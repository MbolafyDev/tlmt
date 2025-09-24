from django.contrib import admin
from .models import Categorie, Produit, ProduitImage, Couleur, Caracteristique


class ProduitImageInline(admin.TabularInline):  # ou StackedInline si tu veux en bloc
    model = ProduitImage
    extra = 3
    fields = ("image", "principale")


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("nom", "categorie", "prix", "prix_original", "avis", "date_ajout")
    list_filter = ("categorie", "date_ajout", "couleurs", "caracteristiques")
    search_fields = ("nom", "description_courte", "description_detaillee")
    prepopulated_fields = {"slug": ("nom",)}
    inlines = [ProduitImageInline]

    # Améliorer la gestion des ManyToMany
    filter_horizontal = ("couleurs", "caracteristiques")


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(ProduitImage)
class ProduitImageAdmin(admin.ModelAdmin):
    list_display = ("produit", "image", "principale")
    list_filter = ("principale",)


@admin.register(Couleur)
class CouleurAdmin(admin.ModelAdmin):
    list_display = ("nom", "code_hex")
    search_fields = ("nom", "code_hex")


@admin.register(Caracteristique)
class CaracteristiqueAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)