from django.shortcuts import render, get_object_or_404, redirect
from article.models import Produit, Categorie
from django.core.paginator import Paginator
from django.http import JsonResponse
from decimal import Decimal
import stripe
from django.conf import settings
from article.utils import render_to_pdf
import random
from .models import Commande, CommandeItem
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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
        pk=produit_id
    )

    # Panier sécurisé
    panier = request.session.get('panier', {})
    if isinstance(panier, list):
        panier = {}
    request.session['panier'] = panier
    total_items = sum(item.get('quantite', 0) for item in panier.values())

    # Si c'est un appel via HTMX/AJAX pour une modale, on renvoie un fragment
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
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "redirect": True,
            "login_url": "/users/login/"
        })

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
        request.session.modified = True

        total_items = sum(item["quantite"] for item in panier.values())

        return JsonResponse({
            "success": True,
            "total_items": total_items
        })

    return JsonResponse({"success": False})


from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
import stripe, random

from article.models import Produit, Categorie
from article.utils import render_to_pdf
from .models import Commande, CommandeItem

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    """
    Page checkout :
    - GET : affiche le panier + formulaire
    - POST (remove_id) : supprime un article du panier
    - POST (paiement) : crée une Session Stripe et redirige vers Stripe
    - GET ?success=true : paiement confirmé => création commande + envoi facture PDF + vidage panier
    """

    if not request.user.is_authenticated:
        return redirect("login")

    # --- Sanitize panier depuis la session ---
    panier = request.session.get('panier', {})
    if isinstance(panier, list) or panier is None:
        panier = {}
    request.session['panier'] = panier  # normalise la session

    # --- Suppression d'un article du panier (formulaire dans checkout.html) ---
    if request.method == "POST" and request.POST.get("remove_id"):
        remove_id = request.POST.get("remove_id")
        if remove_id in panier:
            del panier[remove_id]
            request.session['panier'] = panier
            request.session.modified = True
            messages.success(request, "Article supprimé du panier.")
        # recalcule le total puis on retombe en rendu GET
        total = sum(Decimal(str(item['prix'])) * int(item['quantite']) for item in panier.values()) if panier else Decimal('0')
        return render(request, 'home/checkout.html', {
            'panier': panier,
            'total': total,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        })

    # --- Total courant ---
    total = sum(Decimal(str(item['prix'])) * int(item['quantite']) for item in panier.values()) if panier else Decimal('0')

    # --- Création de la session Stripe Checkout ---
    if request.method == "POST":
        # si ce n'est pas une suppression, on considère que c'est un paiement
        if not panier:
            return JsonResponse({'error': "Votre panier est vide."}, status=400)

        try:
            line_items = []
            for item in panier.values():
                unit_amount = int(Decimal(str(item["prix"])) * 100)  # cents
                line_items.append({
                    'price_data': {
                        'currency': 'eur',  # adapte si nécessaire (ex: 'mga' non supporté par Stripe)
                        'product_data': {'name': item["nom"]},
                        'unit_amount': unit_amount,
                    },
                    'quantity': int(item["quantite"]),
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

    # --- Retour Stripe ---
    if request.GET.get('success') == 'true':
        # Génère un numéro de facture
        numero_facture = f"TEP-{random.randint(1000, 9999)}"

        # Crée la commande (total figé au moment du paiement)
        commande = Commande.objects.create(
            user=request.user,
            numero_facture=numero_facture,
            total=total,
            email=request.user.email
        )

        # Crée les lignes de commande
        for produit_id, item in panier.items():
            produit_obj = get_object_or_404(Produit, id=produit_id)
            CommandeItem.objects.create(
                commande=commande,
                produit=produit_obj,
                quantite=int(item['quantite']),
                prix_unitaire=Decimal(str(item['prix']))
            )

        # Génère le PDF + envoi mail
        context_pdf = {
            'commande': commande,
            'items': commande.items.all(),
            'user': request.user,
        }
        pdf = render_to_pdf('home/includes/factures.html', context_pdf)
        if pdf:
            from django.core.mail import EmailMessage
            email = EmailMessage(
                subject=f"Votre facture {numero_facture}",
                body="Veuillez trouver votre facture en pièce jointe.",
                from_email="no-reply@votre-site.com",
                to=[request.user.email],
            )
            email.attach(f"{numero_facture}.pdf", pdf, "application/pdf")
            email.send()

        # Vide le panier (session + variables locales)
        request.session['panier'] = {}
        request.session.modified = True
        panier = {}
        total = Decimal('0')

        messages.success(request, "Paiement effectué avec succès. Votre facture vous a été envoyée par e-mail.")
        # NOTE : si tu préfères éviter le refresh sur ?success=true, fais plutôt :
        # return redirect('checkout')  # puis affiche un bandeau de succès

    # --- Annulation Stripe ---
    elif request.GET.get('canceled') == 'true':
        messages.error(request, "Paiement annulé ou erreur lors du paiement.")

    # --- Rendu ---
    return render(request, 'home/checkout.html', {
        'panier': panier,
        'total': total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


def categorie_detail(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    produits_list = categorie.produits.all()

    paginator = Paginator(produits_list, 10)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)

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
