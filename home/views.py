from django.shortcuts import render, get_object_or_404, redirect
from article.models import Produit, Categorie
from django.core.paginator import Paginator
from django.http import JsonResponse
from decimal import Decimal
import stripe
from django.conf import settings

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


def checkout(request):
    if not request.user.is_authenticated:
        return redirect("login")

    panier = request.session.get('panier', {})
    if isinstance(panier, list):
        panier = {}
    request.session['panier'] = panier

    total = sum(item['prix'] * item['quantite'] for item in panier.values())
    total_int = int(total)  # Ariary = zero-decimal

    if request.method == "POST":
        remove_id = request.POST.get('remove_id')
        if remove_id:
            panier.pop(remove_id, None)
            request.session['panier'] = panier
            request.session.modified = True
            return redirect('checkout')

        customer_email = request.POST.get("email") or None

        if not panier:
            return JsonResponse({"error": "Panier vide"}, status=400)

        # Créer les line_items pour Stripe Checkout
        line_items = []
        for item in panier.values():
            price = int(Decimal(item['prix']))
            quantity = int(item.get('quantite', 1))
            line_items.append({
                'price_data': {
                    'currency': 'MGA',  # Ariary
                    'product_data': {'name': item.get('nom', 'Produit')},
                    'unit_amount': price,
                },
                'quantity': quantity,
            })

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                customer_email=customer_email,
                success_url=request.build_absolute_uri('/checkout/?success=true'),
                cancel_url=request.build_absolute_uri('/checkout/?canceled=true'),
            )
        except stripe.error.InvalidRequestError as e:
            return JsonResponse({"error": "Stripe InvalidRequestError: " + str(e.user_message or str(e))}, status=400)
        except stripe.error.AuthenticationError as e:
            return JsonResponse({"error": "Stripe AuthenticationError: check your secret key"}, status=401)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": "Erreur Stripe: " + str(e)}, status=500)

        # Renvoie sessionId pour redirectToCheckout côté JS
        return JsonResponse({'sessionId': session.id})

    # GET : affichage page checkout
    # Vider le panier si paiement réussi
    if request.GET.get('success') == 'true':
        request.session['panier'] = {}
        request.session.modified = True

    return render(request, 'home/checkout.html', {
        'panier': request.session.get('panier', {}),
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
