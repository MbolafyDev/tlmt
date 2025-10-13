from django.shortcuts import render
from django.db.models import Q

from article.models import Produit, Categorie
from apropos.models import Apropos, Feature, PointCle
from home.models import Service  # ⚠️ Assure-toi que c’est le bon import

def search_global(request):
    query = request.GET.get("q", "").strip()
    produits = services = categories = apropos = features = points_cles = []

    if query:
        # Produits
        produits = Produit.objects.filter(
            Q(nom__icontains=query) |
            Q(description_courte__icontains=query) |
            Q(description_detaillee__icontains=query)
        ).distinct()

        # Catégories
        categories = Categorie.objects.filter(
            Q(nom__icontains=query)
        ).distinct()

        # Services
        services = Service.objects.filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query) |
            Q(lieu__icontains=query)
        ).distinct()

        # À propos
        apropos = Apropos.objects.filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

        # Features
        features = Feature.objects.filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

        # Points clés
        points_cles = PointCle.objects.filter(
            Q(texte__icontains=query)
        ).distinct()

    context = {
        "query": query,
        "produits": produits,
        "categories": categories,
        "services": services,
        "apropos": apropos,
        "features": features,
        "points_cles": points_cles,
    }
    return render(request, "search_results.html", context)
