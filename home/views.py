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

    if request.method == "POST":
        # Keep existing "remove" behavior
        remove_id = request.POST.get('remove_id')
        if remove_id:
            panier.pop(remove_id, None)
            request.session['panier'] = panier
            request.session.modified = True
            return redirect('checkout')

        # Récupération infos client (optionnelles pour la session)
        customer_email = request.POST.get("email") or None

        # Quick sanity checks
        if not settings.STRIPE_PUBLIC_KEY or not settings.STRIPE_SECRET_KEY:
            return JsonResponse({"error": "Stripe keys not configured (check settings)."}, status=500)

        if not panier:
            return JsonResponse({"error": "Panier vide"}, status=400)

        # Build line_items safely (MGA is zero-decimal: unit_amount must be integer in Ariary)
        line_items = []
        try:
            from decimal import Decimal
            for item in panier.values():
                # ensure price is numeric
                price = Decimal(str(item.get('prix', 0)))
                unit_amount = int(price)  # for MGA (zero-decimal). If you switch to USD, multiply by 100.
                if unit_amount <= 0:
                    return JsonResponse({"error": f"Prix invalide pour l'article: {item.get('nom','')}"}, status=400)

                quantity = int(item.get('quantite', 1))
                line_items.append({
                    'price_data': {
                        'currency': 'MGA',  # keep MGA; if you test with USD, change to 'usd' and multiply amount by 100
                        'product_data': {
                            'name': item.get('nom', 'Produit'),
                        },
                        'unit_amount': unit_amount,
                    },
                    'quantity': quantity,
                })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": "Erreur lors de la préparation des produits: " + str(e)}, status=400)

        # Create session with error handling so we can see the Stripe error message
        try:
            # debug print (supprime en prod)
            print("Stripe: creating session with line_items:", line_items, "customer_email:", customer_email)

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                customer_email=customer_email,
                success_url=request.build_absolute_uri('/') + '?success=true',
                cancel_url=request.build_absolute_uri('/') + '?canceled=true',
            )
        except stripe.error.InvalidRequestError as e:
            # Typical: unsupported currency, bad params, invalid amount, etc.
            return JsonResponse({"error": "Stripe InvalidRequestError: " + str(e.user_message or str(e))}, status=400)
        except stripe.error.AuthenticationError as e:
            return JsonResponse({"error": "Stripe AuthenticationError: check your secret key"}, status=401)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": "Erreur Stripe: " + str(e)}, status=500)

        # Success -> return session id to client
        return JsonResponse({'sessionId': session.id})

    # GET (render page) -- inchangé
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
