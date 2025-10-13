from decimal import Decimal
import random

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from .utils import create_paypal_payment, capture_paypal_order, is_paypal_capture_successful
from django.views.decorators.http import require_GET
from .models import Service, ServiceLike, ServiceComment
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

import stripe

from article.models import Produit, Categorie
from article.utils import render_to_pdf  # ta fonction utilitaire
from .models import Commande, CommandeItem, Service

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# ------------------ VIEWS ------------------

def home(request):
    """
    Page d'accueil : services + produits + compteur panier.
    """
    # Services actifs
    services = Service.objects.prefetch_related("images").filter(is_active=True).order_by('-date_creation')

    # Produits actifs
    produits_list = Produit.objects.prefetch_related("images").filter(is_active=True)
    paginator = Paginator(produits_list, 12)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)

    # Panier
    panier = request.session.get('panier', {})
    if isinstance(panier, list) or panier is None:
        panier = {}
    request.session['panier'] = panier
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())

    return render(request, 'home/home.html', {
        "services": services,
        "produits": produits,
        "total_items": total_items
    })

def ventes(request, slug=None):
    """
    Page vente : tous les produits actifs + pagination + compteur panier + nav-tabs catégories.
    Si slug fourni, filtre par catégorie.
    """
    categories_menu = Categorie.objects.all()

    if slug:
        categorie = get_object_or_404(Categorie, slug=slug)
        produits_list = categorie.produits.filter(is_active=True)
    else:
        categorie = None
        produits_list = Produit.objects.prefetch_related("images").filter(is_active=True)

    paginator = Paginator(produits_list, 12)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)

    panier = request.session.get('panier', {})
    if isinstance(panier, list) or panier is None:
        panier = {}
    request.session['panier'] = panier
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())

    return render(request, 'home/vente.html', {
        "produits": produits,
        "total_items": total_items,
        "categories_menu": categories_menu,
        "slug": slug
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

def produit_detail_resultat(request, produit_id):
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
    template_name = "home/resultat_detail_modal_body.html" if is_htmx else "home/resultat_detail_modal_body.html"

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
    if not request.user.is_authenticated:
        return redirect("login")

    # --- Récupération du panier ---
    panier = request.session.get('panier')
    if not isinstance(panier, dict):
        panier = {}
    request.session['panier'] = panier

    # --- Calcul du total et total_items ---
    total = sum(Decimal(str(item.get('prix', 0))) * int(item.get('quantite', 0)) for item in panier.values()) if panier else Decimal('0')
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())

    # --- Retour depuis PayPal ---
    paypal_token = request.GET.get('token')
    paypal_success = request.GET.get('success')
    if paypal_token and paypal_success:
        try:
            capture_resp = capture_paypal_order(paypal_token)
            if is_paypal_capture_successful(capture_resp):
                numero_facture = f"TEP-{random.randint(1000, 9999)}"
                commande = Commande.objects.create(
                    user=request.user,
                    numero_facture=numero_facture,
                    total=total,
                    email=request.user.email
                )

                for produit_id, item in panier.items():
                    produit_obj = get_object_or_404(Produit, id=produit_id)
                    CommandeItem.objects.create(
                        commande=commande,
                        produit=produit_obj,
                        quantite=int(item.get('quantite', 0)),
                        prix_unitaire=Decimal(str(item.get('prix', 0)))
                    )

                # Générer facture PDF
                context_pdf = {'commande': commande, 'items': commande.items.all(), 'user': request.user}
                pdf_bytes = render_to_pdf('home/includes/factures.html', context_pdf)

                if pdf_bytes:
                    email = EmailMessage(
                        subject=f"Votre facture {numero_facture}",
                        body="Merci pour votre achat ! Votre facture est en pièce jointe.",
                        from_email="no-reply@tlmtstore.com",
                        to=[request.user.email],
                    )
                    email.attach(f"{numero_facture}.pdf", pdf_bytes, "application/pdf")
                    email.send()

                # Vider le panier
                request.session['panier'] = {}
                request.session.modified = True

                messages.success(request, "Paiement PayPal effectué avec succès. Votre facture a été envoyée par e-mail.")
                return redirect('checkout')
            else:
                messages.error(request, "Certaines informations PayPal sont incorrectes. Réessayez.")
                return redirect('checkout')
        except Exception as e:
            messages.error(request, f"Erreur lors de la capture PayPal : {str(e)}")
            return redirect('checkout')

    # --- POST : suppression ou paiement ---
    if request.method == "POST":

        # --- Suppression d'un produit ---
        remove_id = request.POST.get("remove_id")
        if remove_id:
            remove_id = str(remove_id)
            if remove_id in panier:
                del panier[remove_id]
                request.session['panier'] = panier
                request.session.modified = True

            total = sum(Decimal(str(item.get('prix', 0))) * int(item.get('quantite', 0)) for item in panier.values())
            total_items = sum(int(item.get('quantite', 0)) for item in panier.values())

            return redirect('checkout')

        # --- Paiement ---
        mode = request.POST.get("payment_method")
        if not panier:
            return JsonResponse({'error': "Votre panier est vide."}, status=400)

        # --- Stripe ---
        if mode == "stripe":
            try:
                line_items = []
                for item in panier.values():
                    unit_amount = int(Decimal(str(item.get("prix", 0))) * 100)
                    line_items.append({
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {'name': item.get("nom", "Article")},
                            'unit_amount': unit_amount,
                        },
                        'quantity': int(item.get("quantite", 0)),
                    })

                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=request.build_absolute_uri('?stripe=1&success=true'),
                    cancel_url=request.build_absolute_uri('?stripe=1&canceled=true'),
                )
                return JsonResponse({'sessionId': session.id})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

        # --- PayPal ---
        elif mode == "paypal":
            try:
                # --- Conversion Ariary → USD ---
                MGA_TO_USD = 0.00022
                total_usd = float(total) * MGA_TO_USD

                # PayPal sandbox refuse 0.00 USD
                if total_usd < 0.01:
                    total_usd = 0.01

                total_usd = round(total_usd, 2)  # obligatoire pour PayPal (2 décimales minimum)

                # --- URLs complètes ---
                if "localhost" in request.get_host() or "127.0.0.1" in request.get_host():
                    # Utiliser ngrok si en local
                    base_url = "https://xxxxxx.ngrok.io"  # <- à remplacer par ton URL ngrok
                else:
                    base_url = request.build_absolute_uri("/").rstrip("/")

                return_url = f"{base_url}/checkout?success=true"
                cancel_url = f"{base_url}/checkout?canceled=true"

                paypal_resp = create_paypal_payment(total_usd, 'USD', return_url, cancel_url)

                approval_url = paypal_resp.get('approval_url')
                if approval_url:
                    return JsonResponse({'approval_url': approval_url})
                else:
                    return JsonResponse({'error': 'Impossible de créer le paiement PayPal.'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

        else:
            return JsonResponse({'error': 'Mode de paiement non valide.'}, status=400)

    # --- Capture Stripe (success=true) ---
    if request.GET.get('stripe') == '1' and request.GET.get('success'):
        numero_facture = f"TEP-{random.randint(1000, 9999)}"
        commande = Commande.objects.create(
            user=request.user,
            numero_facture=numero_facture,
            total=total,
            email=request.user.email
        )

        for produit_id, item in panier.items():
            produit_obj = get_object_or_404(Produit, id=produit_id)
            CommandeItem.objects.create(
                commande=commande,
                produit=produit_obj,
                quantite=int(item.get('quantite', 0)),
                prix_unitaire=Decimal(str(item.get('prix', 0)))
            )

        context_pdf = {'commande': commande, 'items': commande.items.all(), 'user': request.user}
        pdf_bytes = render_to_pdf('home/includes/factures.html', context_pdf)

        if pdf_bytes:
            email = EmailMessage(
                subject=f"Votre facture {numero_facture}",
                body="Merci pour votre achat ! Votre facture est en pièce jointe.",
                from_email="no-reply@tlmtstore.com",
                to=[request.user.email],
            )
            email.attach(f"{numero_facture}.pdf", pdf_bytes, "application/pdf")
            email.send()

        request.session['panier'] = {}
        request.session.modified = True

        messages.success(request, "Paiement Stripe effectué avec succès.")
        return redirect('checkout')

    # --- Rendu du template ---
    return render(request, 'home/checkout.html', {
        'panier': panier,
        'total': total,
        'total_items': total_items,
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

@require_GET
def voir_plus_service(request, service_id):
    """
    Renvoie le modal complet d'un service pour affichage via AJAX.
    """
    service = get_object_or_404(Service.objects.prefetch_related("images"), pk=service_id)
    html_modal = render_to_string('home/_modal_service.html', {'service': service}, request=request)
    return JsonResponse({'html': html_modal})

@login_required
@require_POST
def like_service(request):
    service_id = request.POST.get('service_id')
    service = get_object_or_404(Service, id=service_id)
    
    # Like ou dislike uniquement pour ce service et cet utilisateur
    like, created = ServiceLike.objects.get_or_create(user=request.user, service=service)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': service.likes_count
    })


# ======== Ajouter un commentaire ========
@login_required
@require_POST
def comment_service(request):
    service_id = request.POST.get('service_id')
    content = request.POST.get('content')
    service = get_object_or_404(Service, id=service_id)
    
    if content.strip() == "":
        return JsonResponse({'success': False, 'error': 'Le commentaire ne peut pas être vide.'})
    
    # Création du commentaire lié à l'utilisateur
    comment = ServiceComment.objects.create(user=request.user, service=service, content=content)
    
    return JsonResponse({
        'success': True,
        'comment_id': comment.id,
        'username': comment.user.username,
        'content': comment.content,
        'comments_count': service.comments_count
    })


# ======== Récupérer tous les commentaires d’un service ========
@login_required
def get_comments_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    # Récupère uniquement les commentaires liés à ce service
    comments = service.comments.select_related('user').order_by('created_at')
    
    # On renvoie la liste des commentaires avec l'utilisateur
    comments_data = [{
        'username': c.user.username,
        'content': c.content,
        'created_at': c.created_at.strftime("%d/%m/%Y %H:%M")
    } for c in comments]
    
    return JsonResponse({'comments': comments_data})