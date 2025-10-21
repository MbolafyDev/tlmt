from decimal import Decimal
import random
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required

from article.models import Produit, Categorie
from article.utils import render_to_pdf
from .models import Service, ServiceLike, ServiceComment, Commande, CommandeItem, CommandeDetail

# ------------------ VIEWS ------------------

def home(request):
    services = Service.objects.prefetch_related("images").filter(is_active=True).order_by('-date_creation')
    produits_list = Produit.objects.prefetch_related("images").filter(is_active=True)
    paginator = Paginator(produits_list, 12)
    produits = paginator.get_page(request.GET.get('page'))
    panier = request.session.get('panier', {}) or {}
    request.session['panier'] = panier
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())
    return render(request, 'home/home.html', {
        "services": services,
        "produits": produits,
        "total_items": total_items,
        "request": request,
    })

def ventes(request, slug=None):
    categories_menu = Categorie.objects.all()
    if slug:
        categorie = get_object_or_404(Categorie, slug=slug)
        produits_list = categorie.produits.filter(is_active=True)
    else:
        categorie = None
        produits_list = Produit.objects.prefetch_related("images").filter(is_active=True)
    paginator = Paginator(produits_list, 12)
    produits = paginator.get_page(request.GET.get('page'))
    panier = request.session.get('panier', {}) or {}
    request.session['panier'] = panier
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())
    return render(request, 'home/vente.html', {
        "produits": produits,
        "total_items": total_items,
        "categories_menu": categories_menu,
        "slug": slug
    })

def produit_detail(request, produit_id):
    produit = get_object_or_404(
        Produit.objects.prefetch_related("images", "caracteristiques", "couleurs"),
        pk=produit_id
    )
    panier = request.session.get('panier', {}) or {}
    request.session['panier'] = panier
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())
    is_htmx = request.headers.get("HX-Request") == "true" or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    template_name = "home/_detail_modal_body.html" if is_htmx else "home/detail.html"
    return render(request, template_name, {'produit': produit, 'total_items': total_items})

def produit_detail_resultat(request, produit_id):
    produit = get_object_or_404(
        Produit.objects.prefetch_related("images", "caracteristiques", "couleurs"),
        pk=produit_id
    )
    panier = request.session.get('panier', {}) or {}
    request.session['panier'] = panier
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())
    template_name = "home/resultat_detail_modal_body.html"
    return render(request, template_name, {'produit': produit, 'total_items': total_items})

def ajouter_au_panier(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "redirect": True, "login_url": "/users/login/"})
    if request.method == "POST":
        produit_id = request.POST.get("produit_id")
        quantite = int(request.POST.get("quantite", 1) or 1)
        produit = get_object_or_404(Produit, id=produit_id)
        panier = request.session.get("panier", {}) or {}
        key = str(produit_id)
        if key in panier:
            panier[key]["quantite"] += quantite
        else:
            image_url = "/static/images/default.png"
            first_img = getattr(produit.images.first(), "image", None)
            if first_img and getattr(first_img, "url", None):
                image_url = first_img.url
            panier[key] = {
                "nom": produit.nom,
                "prix": float(produit.prix),
                "quantite": quantite,
                "image": image_url,
            }
        request.session["panier"] = panier
        request.session.modified = True
        total_items = sum(int(item.get("quantite", 0)) for item in panier.values())
        return JsonResponse({"success": True, "total_items": total_items})
    return JsonResponse({"success": False})

@login_required
def checkout(request):
    panier = request.session.get('panier', {}) or {}
    total = sum(Decimal(str(item.get('prix', 0))) * int(item.get('quantite', 0)) for item in panier.values())
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())

    # POST : paiement ou suppression
    if request.method == "POST":
        remove_id = request.POST.get("remove_id")
        if remove_id:
            panier.pop(str(remove_id), None)
            request.session['panier'] = panier
            request.session.modified = True
            return redirect('checkout')

        mode = request.POST.get("payment_method")
        if not panier:
            messages.error(request, "Votre panier est vide.")
            return redirect('checkout')

        # Paiement espèces / Mobile Money
        if mode in ["espece", "mvola", "airtel", "orange"]:
            request.session['payment_mode'] = mode
            return redirect('info_commande')

    return render(request, 'home/checkout.html', {
        'panier': panier,
        'total': total,
        'total_items': total_items
    })

@login_required
def info_commande(request):
    panier = request.session.get('panier', {}) or {}
    total = sum(Decimal(str(item.get('prix', 0))) * int(item.get('quantite', 0)) for item in panier.values())
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())
    mode = request.session.get('payment_mode')

    if request.method == "POST":
        nom_complet = request.POST.get('nom_complet')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        adresse_livraison = request.POST.get('adresse_livraison')
        ville = request.POST.get('ville')
        commentaire = request.POST.get('commentaire')

        numero_facture = f"TEP-{random.randint(1000, 9999)}"
        commande = Commande.objects.create(
            user=request.user,
            numero_facture=numero_facture,
            total=total,
            email=email,
            mode_paiement=mode
        )
        for produit_id, item in panier.items():
            produit_obj = get_object_or_404(Produit, id=produit_id)
            CommandeItem.objects.create(
                commande=commande,
                produit=produit_obj,
                quantite=int(item.get('quantite', 0)),
                prix_unitaire=Decimal(str(item.get('prix', 0)))
            )
        CommandeDetail.objects.create(
            commande=commande,
            nom_complet=nom_complet,
            email=email,
            contact=contact,
            adresse_livraison=adresse_livraison,
            ville=ville,
            commentaire=commentaire
        )

        request.session['panier'] = {}
        request.session['payment_mode'] = None
        messages.success(request, f"Commande {numero_facture} enregistrée avec succès ! Mode de paiement : {mode}")
        return redirect('home')

    return render(request, 'home/includes/info.html', {
        'panier': panier,
        'total': total,
        'total_items': total_items,
        'mode': mode
    })

def categorie_detail(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    produits_list = categorie.produits.all()
    paginator = Paginator(produits_list, 10)
    produits = paginator.get_page(request.GET.get('page'))
    panier = request.session.get('panier', {}) or {}
    total_items = sum(int(item.get('quantite', 0)) for item in panier.values())
    return render(request, 'home/home.html', {'produits': produits, 'categorie': categorie, 'total_items': total_items})

@require_GET
def voir_plus_service(request, service_id):
    service = get_object_or_404(Service.objects.prefetch_related("images"), pk=service_id)
    html_modal = render_to_string('home/_modal_service.html', {'service': service}, request=request)
    return JsonResponse({'html': html_modal})

@login_required
@require_POST
def like_service(request):
    service = get_object_or_404(Service, id=request.POST.get('service_id'))
    like, created = ServiceLike.objects.get_or_create(user=request.user, service=service)
    if not created: like.delete(); liked=False
    else: liked=True
    return JsonResponse({'liked': liked, 'likes_count': service.likes_count})

@login_required
@require_POST
def comment_service(request):
    service = get_object_or_404(Service, id=request.POST.get('service_id'))
    content = request.POST.get('content')
    if not content.strip(): return JsonResponse({'success': False, 'error': 'Le commentaire ne peut pas être vide.'})
    comment = ServiceComment.objects.create(user=request.user, service=service, content=content)
    return JsonResponse({'success': True, 'comment_id': comment.id, 'username': comment.user.username, 'content': comment.content, 'comments_count': service.comments_count})

@login_required
def get_comments_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    comments_data = []

    # On ne récupère que les commentaires parent (sans parent)
    parent_comments = service.comments.filter(parent__isnull=True).select_related('user').order_by('created_at')
    for c in parent_comments:
        # Récupérer les réponses du commentaire
        replies = [{
            'username': r.user.username,
            'content': r.content,
            'created_at': r.created_at.strftime("%d/%m/%Y %H:%M")
        } for r in service.comments.filter(parent=c).select_related('user').order_by('created_at')]

        comments_data.append({
            'id': c.id,
            'username': c.user.username,
            'content': c.content,
            'created_at': c.created_at.strftime("%d/%m/%Y %H:%M"),
            'replies': replies
        })

    return JsonResponse({'comments': comments_data})

@login_required
@require_POST
def reply_comment_service(request):
    parent_comment = get_object_or_404(ServiceComment, id=request.POST.get('comment_id'))
    content = request.POST.get('content')
    if not content.strip(): return JsonResponse({'success': False, 'error': 'Le message ne peut pas être vide.'})
    reply = ServiceComment.objects.create(user=request.user, service=parent_comment.service, content=content, parent=parent_comment)
    return JsonResponse({'success': True, 'username': reply.user.username, 'content': reply.content})
