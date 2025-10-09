from decimal import Decimal
import random

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

import stripe

from article.models import Produit, Categorie
from article.utils import render_to_pdf  # ta fonction utilitaire
from .models import Commande, CommandeItem

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# ------------------ VIEWS ------------------

def home(request):
    """
    Page d'accueil : liste paginée des produits + compteur panier.
    """
    produits_list = Produit.objects.prefetch_related("images").filter(is_active=True)
    paginator = Paginator(produits_list, 12)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)

    # Panier: garantir un dict
    panier = request.session.get('panier', {})
    if isinstance(panier, list) or panier is None:
        panier = {}
    request.session['panier'] = panier

    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())

    return render(request, 'home/home.html', {
        "produits": produits,
        "total_items": total_items
    })


def produit_detail(request, produit_id):
    """
    Détail produit ; renvoie un fragment si appel HTMX/AJAX (modale).
    """
    produit = get_object_or_404(
        Produit.objects.prefetch_related("images", "caracteristiques", "couleurs"),
        pk=produit_id
    )

    panier = request.session.get('panier', {})
    if isinstance(panier, list) or panier is None:
        panier = {}
    request.session['panier'] = panier

    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())

    is_htmx = (
        request.headers.get("HX-Request") == "true"
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )
    template_name = "home/_detail_modal_body.html" if is_htmx else "home/detail.html"

    return render(request, template_name, {
        'produit': produit,
        'total_items': total_items
    })


def ajouter_au_panier(request):
    """
    Ajoute un produit au panier en session. Répond en JSON.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "redirect": True,
            "login_url": "/users/login/"
        })

    if request.method == "POST":
        produit_id = request.POST.get("produit_id")
        try:
            quantite = int(request.POST.get("quantite", 1))
        except (TypeError, ValueError):
            quantite = 1

        produit = get_object_or_404(Produit, id=produit_id)

        panier = request.session.get("panier", {})
        if isinstance(panier, list) or panier is None:
            panier = {}

        # Toujours stocker la clé en str (cohérence session)
        key = str(produit_id)

        if key in panier:
            panier[key]["quantite"] = int(panier[key].get("quantite", 0)) + quantite
        else:
            image_url = "/static/images/default.png"
            first_img = getattr(produit.images.first(), "image", None)
            if first_img and getattr(first_img, "url", None):
                image_url = first_img.url

            panier[key] = {
                "nom": produit.nom,
                "prix": float(produit.prix),
                "prix_original": float(getattr(produit, "prix_original", produit.prix)),
                "quantite": quantite,
                "image": image_url,
            }

        request.session["panier"] = panier
        request.session.modified = True

        total_items = sum(int(item.get("quantite", 0)) for item in panier.values())

        return JsonResponse({
            "success": True,
            "total_items": total_items
        })

    return JsonResponse({"success": False})


def checkout(request):
    """
    Page checkout :
    - GET : affiche le panier + formulaire
    - POST (remove_id) : supprime un article du panier
    - POST (paiement) : crée une Session Stripe et renvoie l'id de session
    - GET ?success=true : paiement confirmé => création commande + envoi facture PDF + vidage panier
    - GET ?canceled=true : paiement annulé
    """
    if not request.user.is_authenticated:
        return redirect("login")

    # Panier propre depuis la session
    panier = request.session.get('panier', {})
    if isinstance(panier, list) or panier is None:
        panier = {}
    request.session['panier'] = panier

    # Suppression d'un article du panier
    if request.method == "POST" and request.POST.get("remove_id"):
        remove_id = str(request.POST.get("remove_id"))
        if remove_id in panier:
            del panier[remove_id]
            request.session['panier'] = panier
            request.session.modified = True
            messages.success(request, "Article supprimé du panier.")

        total = sum(
            Decimal(str(item.get('prix', 0))) * int(item.get('quantite', 0))
            for item in panier.values()
        ) if panier else Decimal('0')

        return render(request, 'home/checkout.html', {
            'panier': panier,
            'total': total,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        })

    # Total courant
    total = sum(
        Decimal(str(item.get('prix', 0))) * int(item.get('quantite', 0))
        for item in panier.values()
    ) if panier else Decimal('0')

    # Démarrer un paiement Stripe
    if request.method == "POST":
        if not panier:
            return JsonResponse({'error': "Votre panier est vide."}, status=400)

        try:
            line_items = []
            for item in panier.values():
                unit_amount = int(Decimal(str(item.get("prix", 0))) * 100)  # en cents
                line_items.append({
                    'price_data': {
                        'currency': 'eur',  # adapter si besoin (MGA non supporté par Stripe)
                        'product_data': {'name': item.get("nom", "Article")},
                        'unit_amount': unit_amount,
                    },
                    'quantity': int(item.get("quantite", 0)),
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri('?success=true'),
                cancel_url=request.build_absolute_uri('?canceled=true'),
            )
            return JsonResponse({'sessionId': session.id})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Retour succès depuis Stripe
    if request.GET.get('success') == 'true':
        numero_facture = f"TEP-{random.randint(1000, 9999)}"

        # Crée la commande (total figé au moment du paiement)
        commande = Commande.objects.create(
            user=request.user,
            numero_facture=numero_facture,
            total=total,
            email=request.user.email
        )

        # Lignes de commande
        for produit_id, item in panier.items():
            produit_obj = get_object_or_404(Produit, id=produit_id)
            CommandeItem.objects.create(
                commande=commande,
                produit=produit_obj,
                quantite=int(item.get('quantite', 0)),
                prix_unitaire=Decimal(str(item.get('prix', 0)))
            )

        # Génère le PDF + envoi mail
        context_pdf = {
            'commande': commande,
            'items': commande.items.all(),
            'user': request.user,
        }

        # Compat : si ta util accepte base_url (WeasyPrint), on la passe ; sinon on retombe sur l'appel simple
        pdf_bytes = None
        try:
            pdf_bytes = render_to_pdf('home/includes/factures.html', context_pdf,
                                      base_url=request.build_absolute_uri('/'))
        except TypeError:
            # signature sans base_url
            pdf_bytes = render_to_pdf('home/includes/factures.html', context_pdf)

        if pdf_bytes:
            email = EmailMessage(
                subject=f"Votre facture {numero_facture}",
                body="Veuillez trouver votre facture en pièce jointe.",
                from_email="no-reply@votre-site.com",
                to=[request.user.email],
            )
            email.attach(f"{numero_facture}.pdf", pdf_bytes, "application/pdf")
            email.send()

        # Vider le panier
        request.session['panier'] = {}
        request.session.modified = True

        messages.success(
            request,
            "Paiement effectué avec succès. Votre facture vous a été envoyée par e-mail."
        )
        # Rendre la page checkout avec panier vide
        panier = {}
        total = Decimal('0')

    elif request.GET.get('canceled') == 'true':
        messages.error(request, "Paiement annulé ou erreur lors du paiement.")

    # Rendu
    return render(request, 'home/checkout.html', {
        'panier': panier,
        'total': total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


def categorie_detail(request, slug):
    """
    Liste des produits d'une catégorie (pagination) + compteur panier.
    """
    categorie = get_object_or_404(Categorie, slug=slug)
    produits_list = categorie.produits.all()

    paginator = Paginator(produits_list, 10)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)

    panier = request.session.get('panier', {})
    if isinstance(panier, list) or panier is None:
        panier = {}
    request.session['panier'] = panier

    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())

    return render(request, 'home/home.html', {
        'produits': produits,
        'categorie': categorie,
        'total_items': total_items
    })
