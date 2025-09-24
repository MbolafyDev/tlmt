from django.shortcuts import render, get_object_or_404, redirect
from article.models import Produit, Categorie
from django.core.paginator import Paginator
from django.http import JsonResponse
from decimal import Decimal

# ------------------ VIEWS ------------------

def home(request):
    produits_list = Produit.objects.prefetch_related("images").all()
    paginator = Paginator(produits_list, 10)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)

    # Récupérer le panier et forcer dict
    panier = request.session.get('panier', {})
    if isinstance(panier, list):
        panier = {}
    request.session['panier'] = panier

    total_items = sum(item['quantite'] for item in panier.values())

    return render(request, 'home/home.html', {
        "produits": produits,
        "total_items": total_items
    })


def produit_detail(request, produit_id):
    produit = get_object_or_404(
        Produit.objects.prefetch_related("images", "caracteristiques", "couleurs"),
        id=produit_id
    )

    # Panier sécurisé
    panier = request.session.get('panier', {})
    if isinstance(panier, list):
        panier = {}
    request.session['panier'] = panier

    total_items = sum(item['quantite'] for item in panier.values())

    return render(request, 'home/detail.html', {
        'produit': produit,
        'total_items': total_items
    })


def ajouter_au_panier(request):
    if request.method == "POST":
        produit_id = request.POST.get("produit_id")
        quantite = int(request.POST.get("quantite", 1))

        produit = get_object_or_404(Produit, id=produit_id)

        panier = request.session.get("panier", {})
        if isinstance(panier, list):
            panier = {}

        if produit_id in panier:
            panier[produit_id]["quantite"] += quantite
        else:
            panier[produit_id] = {
                "nom": produit.nom,
                "prix": float(produit.prix),
                "prix_original": float(produit.prix_original),
                "quantite": quantite,
                "image": produit.images.first().image.url if produit.images.exists() else "/static/images/default.png"
            }

        request.session["panier"] = panier
        request.session.modified = True  # important pour sauvegarder la session

        total_items = sum(item["quantite"] for item in panier.values())

        return JsonResponse({
            "success": True,
            "total_items": total_items
        })

    return JsonResponse({"success": False})


def checkout(request):
    panier = request.session.get('panier', {})
    if isinstance(panier, list):
        panier = {}
    request.session['panier'] = panier

    total = sum(item['prix'] * item['quantite'] for item in panier.values())

    if request.method == "POST":
        remove_id = request.POST.get('remove_id')
        if remove_id:
            panier.pop(remove_id, None)
            request.session['panier'] = panier
            request.session.modified = True
            return redirect('checkout')

        # Traitement de commande (simulé)
        request.session['panier'] = {}
        request.session.modified = True
        # Remplacez 'commande_confirmee' par la vue que vous souhaitez réellement
        return redirect('home')  

    return render(request, 'home/checkout.html', {
        'panier': panier,  # Passez le dict complet
        'total': total
    })


def categorie_detail(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    produits_list = categorie.produits.all()

    paginator = Paginator(produits_list, 10)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)

    # Panier sécurisé
    panier = request.session.get('panier', {})
    if isinstance(panier, list):
        panier = {}
    request.session['panier'] = panier

    total_items = sum(item['quantite'] for item in panier.values())

    return render(request, 'home/home.html', {
        'produits': produits,
        'categorie': categorie,
        'total_items': total_items
    })
