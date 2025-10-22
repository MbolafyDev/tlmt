# tlmt/configuration/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from users.models import CustomUser
from .forms import UserValidationForm, ProduitForm, ProduitImageForm
from common.decorators import admin_required
from article.models import Produit, ProduitImage, Categorie, Caracteristique
from plomberie.models import AppareilSanitaire
from .forms import AppareilSanitaireForm
from home.forms import ServiceForm, ServiceImageFormSet
from home.models import Service, ServiceImage
from home.models import Commande, CommandeItem
from django.contrib.admin.views.decorators import staff_member_required
from contact.models import ContactMessage
from django.http import JsonResponse
from django.views.decorators.http import require_POST


# ---------------- Users ----------------
@admin_required
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, "configuration/user_list.html", {"users": users})


@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = UserValidationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"L’utilisateur {user.username} a été mis à jour avec succès.")
            return redirect("user_list")
    else:
        form = UserValidationForm(instance=user)
    return render(request, "configuration/edit_user.html", {"form": form, "user": user})

# ---------------- Users ----------------
@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, f"L’utilisateur {user.username} a été supprimé avec succès.")
        return redirect("user_list")
    return render(request, "configuration/includes/user_confirm_delete.html", {"user": user})


# ---------------- Articles ----------------
@admin_required
def produit_list(request):
    # Recherche simple via ?q=
    q = (request.GET.get("q") or "").strip()
    qs = (
        Produit.objects.all()
        .prefetch_related("images", "caracteristiques")
        .select_related("categorie")
        .order_by("-id")
    )
    if q:
        qs = qs.filter(
            Q(nom__icontains=q)
            | Q(description_courte__icontains=q)
            | Q(description_detaillee__icontains=q)
            | Q(categorie__nom__icontains=q)
        )

    paginator = Paginator(qs, 12)
    page = request.GET.get("page", 1)
    try:
        produits = paginator.page(page)
    except PageNotAnInteger:
        produits = paginator.page(1)
    except EmptyPage:
        produits = paginator.page(paginator.num_pages)

    return render(
        request,
        "configuration/produit_list.html",
        {
            "produits": produits,
            "is_paginated": paginator.num_pages > 1,
            "q": q,
        },
    )


@admin_required
def produit_add(request):
    if request.method == "POST":
        form = ProduitForm(request.POST)
        files = request.FILES.getlist("images")
        if form.is_valid():
            produit = form.save()  # commit=True -> M2M OK
            for f in files:
                ProduitImage.objects.create(produit=produit, image=f)
            messages.success(request, f"Produit '{produit.nom}' ajouté avec succès.")
            return redirect("produit_list")
    else:
        form = ProduitForm()
    return render(
        request,
        "configuration/produit_form.html",
        {"form": form, "title": "Ajouter un produit"},
    )


@admin_required
def produit_edit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        files = request.FILES.getlist("images")
        if form.is_valid():
            produit = form.save()  # M2M actualisées
            for f in files:
                ProduitImage.objects.create(produit=produit, image=f)
            messages.success(request, f"Produit '{produit.nom}' mis à jour avec succès.")
            return redirect("produit_list")
    else:
        form = ProduitForm(instance=produit)
    return render(
        request,
        "configuration/produit_form.html",
        {"form": form, "title": f"Modifier le produit : {produit.nom}"},
    )


@admin_required
def produit_delete(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produit.delete()
    messages.success(request, f"Produit '{produit.nom}' supprimé avec succès.")
    return redirect("produit_list")


@admin_required
def produit_detail(request, produit_id):
    produit = get_object_or_404(
        Produit.objects.prefetch_related("images", "caracteristiques").select_related("categorie"),
        id=produit_id,
    )
    # On s'appuie sur ProduitForm pour exposer toutes les infos "éditables"
    form = ProduitForm(instance=produit)

    details = []
    for name, field in form.fields.items():
        label = field.label or name.replace("_", " ").title()
        display_getter = f"get_{name}_display"
        if hasattr(produit, display_getter):
            value = getattr(produit, display_getter)()
        else:
            attr = getattr(produit, name, None)
            if hasattr(attr, "all"):  # ManyToMany
                value = ", ".join(str(x) for x in attr.all())
            else:
                value = attr
        if value in (None, ""):
            value = "—"
        details.append((label, value))

    return render(
        request,
        "configuration/includes/produit_detail_modal.html",
        {"produit": produit, "details": details},
    )


# ---------------- Catégorie ----------------
@admin_required
def categorie_list(request):
    categories = Categorie.objects.all()
    return render(request, "configuration/categorie_list.html", {"categories": categories})


@admin_required
def categorie_add(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        if nom:
            Categorie.objects.create(nom=nom)
            messages.success(request, f"Catégorie '{nom}' ajoutée avec succès.")
            return redirect("categorie_list")
    return render(request, "configuration/categorie_form.html", {"title": "Ajouter une catégorie"})


@admin_required
def categorie_edit(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    if request.method == "POST":
        nom = request.POST.get("nom")
        if nom:
            categorie.nom = nom
            categorie.save()
            messages.success(request, f"Catégorie '{nom}' mise à jour avec succès.")
            return redirect("categorie_list")
    return render(
        request,
        "configuration/categorie_form.html",
        {"categorie": categorie, "title": f"Modifier la catégorie : {categorie.nom}"},
    )


@admin_required
def categorie_delete(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    categorie.delete()
    messages.success(request, f"Catégorie '{categorie.nom}' supprimée avec succès.")
    return redirect("categorie_list")


# ---------------- Caractéristique ----------------
@admin_required
def caracteristique_list(request):
    caracteristiques = Caracteristique.objects.all()
    return render(
        request, "configuration/caracteristique_list.html", {"caracteristiques": caracteristiques}
    )


@admin_required
def caracteristique_add(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        if nom:
            Caracteristique.objects.create(nom=nom)
            messages.success(request, f"Caractéristique '{nom}' ajoutée avec succès.")
            return redirect("caracteristique_list")
    return render(
        request, "configuration/caracteristique_form.html", {"title": "Ajouter une caractéristique"}
    )


@admin_required
def caracteristique_edit(request, caracteristique_id):
    caracteristique = get_object_or_404(Caracteristique, id=caracteristique_id)
    if request.method == "POST":
        nom = request.POST.get("nom")
        if nom:
            caracteristique.nom = nom
            caracteristique.save()
            messages.success(request, f"Caractéristique '{nom}' mise à jour avec succès.")
            return redirect("caracteristique_list")
    return render(
        request,
        "configuration/caracteristique_form.html",
        {"caracteristique": caracteristique, "title": f"Modifier la caractéristique : {caracteristique.nom}"},
    )


@admin_required
def caracteristique_delete(request, caracteristique_id):
    caracteristique = get_object_or_404(Caracteristique, id=caracteristique_id)
    caracteristique.delete()
    messages.success(request, f"Caractéristique '{caracteristique.nom}' supprimée avec succès.")
    return redirect("caracteristique_list")

@admin_required
def appareil_add(request):
    if request.method == "POST":
        form = AppareilSanitaireForm(request.POST, request.FILES)
        if form.is_valid():
            appareil = form.save()
            messages.success(request, f"L’appareil sanitaire '{appareil.nom}' a été ajouté avec succès.")
            return redirect("appareil_list")
    else:
        form = AppareilSanitaireForm()
    return render(
        request,
        "configuration/appareil_form.html",
        {"form": form, "title": "Ajouter un appareil sanitaire"},
    )


@admin_required
def appareil_list(request):
    appareils = AppareilSanitaire.objects.all().order_by("nom")
    return render(
        request,
        "configuration/appareil_list.html",
        {"appareils": appareils, "title": "Liste des appareils sanitaires"},
    )




@admin_required
def appareil_delete(request, appareil_id):
    appareil = get_object_or_404(AppareilSanitaire, id=appareil_id)
    appareil.delete()
    messages.success(request, f"L’appareil sanitaire '{appareil.nom}' a été supprimé avec succès.")
    return redirect("appareil_list")

@admin_required
def appareil_edit(request, appareil_id):
    appareil = get_object_or_404(AppareilSanitaire, id=appareil_id)
    
    if request.method == "POST":
        form = AppareilSanitaireForm(request.POST, request.FILES, instance=appareil)
        if form.is_valid():
            form.save()
            messages.success(request, f"L’appareil '{appareil.nom}' a été modifié avec succès.")
            return redirect("appareil_list")
    else:
        form = AppareilSanitaireForm(instance=appareil)

    return render(
        request,
        "configuration/appareil_edit.html",
        {"form": form, "title": f"Modifier {appareil.nom}"}
    )

@admin_required
def service_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Service.objects.prefetch_related("images").order_by("-id")

    if q:
        qs = qs.filter(
            Q(titre__icontains=q) |
            Q(description__icontains=q) |
            Q(lieu__icontains=q)
        )

    paginator = Paginator(qs, 12)
    page = request.GET.get("page", 1)
    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        services = paginator.page(1)
    except EmptyPage:
        services = paginator.page(paginator.num_pages)

    return render(
        request,
        "configuration/service_list.html",
        {"services": services, "is_paginated": paginator.num_pages > 1, "q": q},
    )


@admin_required
def service_add(request):
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            # On sauvegarde le parent pour obtenir un PK
            service = form.save()

            # ⚠️ Formset RE-binder avec l'instance parent
            formset = ServiceImageFormSet(request.POST, request.FILES, instance=service)

            if formset.is_valid():
                # Sauvegarde standard : gère ajouts/suppressions
                instances = formset.save(commit=False)
                for img in instances:
                    img.service = service
                    img.save()
                # Supprimer les images marquées DELETE
                for obj in formset.deleted_objects:
                    obj.delete()

                messages.success(request, f"Service '{service.titre}' ajouté avec succès.")
                return redirect('service_list')
            else:
                messages.error(request, "Veuillez corriger les erreurs ci-dessous (images).")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = ServiceForm()
        formset = ServiceImageFormSet()  # vierge

    return render(request, 'configuration/service_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Ajouter un service',
        # utile pour l'affichage conditionnel d'images
        'service': None,
    })


@admin_required
def service_edit(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES, instance=service)
        # ⚠️ inutile de passer queryset=..., l'inline formset s'en charge
        formset = ServiceImageFormSet(request.POST, request.FILES, instance=service)

        if form.is_valid() and formset.is_valid():
            service = form.save()

            instances = formset.save(commit=False)
            for img in instances:
                img.service = service
                img.save()

            for obj in formset.deleted_objects:
                obj.delete()

            messages.success(request, f"Service '{service.titre}' mis à jour avec succès.")
            return redirect('service_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ServiceForm(instance=service)
        formset = ServiceImageFormSet(instance=service)

    return render(request, 'configuration/service_form.html', {
        'form': form,
        'formset': formset,
        'title': f"Modifier le service : {service.titre}",
        'service': service,
    })





@admin_required
def service_delete(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    messages.success(request, f"Service '{service.titre}' supprimé avec succès.")
    return redirect('service_list')


@admin_required
def service_detail(request, service_id):
    service = get_object_or_404(Service.objects.prefetch_related('images'), id=service_id)
    return render(request, 'configuration/service_detail_modal.html', {'service': service})

# ---------------- Journal des commandes ----------------
@admin_required
def journal_commandes(request):
    q = (request.GET.get("q") or "").strip()
    view_mode = request.GET.get("view", "table")  # table par défaut

    # Trier par date_creation décroissante pour afficher les nouvelles commandes en premier
    commandes = Commande.objects.select_related('user')\
        .prefetch_related('items__produit')\
        .order_by('-date_creation')

    if q:
        commandes = commandes.filter(
            Q(numero_facture__icontains=q) |
            Q(user__username__icontains=q) |
            Q(email__icontains=q)
        )

    paginator = Paginator(commandes, 15)
    page = request.GET.get("page", 1)
    try:
        commandes_page = paginator.page(page)
    except PageNotAnInteger:
        commandes_page = paginator.page(1)
    except EmptyPage:
        commandes_page = paginator.page(paginator.num_pages)

    return render(request, "configuration/journal_commandes.html", {
        "commandes": commandes_page,
        "is_paginated": paginator.num_pages > 1,
        "q": q,
        "view_mode": view_mode,
    })

# ---------------- Contact Messages ----------------
@admin_required
def contact_messages(request):
    q = (request.GET.get("q") or "").strip()
    view_mode = request.GET.get("view", "table")

    qs = ContactMessage.objects.all().order_by('-date_envoi')
    if q:
        qs = qs.filter(
            Q(nom__icontains=q) |
            Q(email__icontains=q) |
            Q(sujet__icontains=q) |
            Q(message__icontains=q)
        )

    paginator = Paginator(qs, 15)
    page = request.GET.get("page", 1)
    try:
        messages_page = paginator.page(page)
    except PageNotAnInteger:
        messages_page = paginator.page(1)
    except EmptyPage:
        messages_page = paginator.page(paginator.num_pages)

    return render(request, "configuration/contact_message_list.html", {
        "messages_page": messages_page,
        "is_paginated": paginator.num_pages > 1,
        "q": q,
        "view_mode": view_mode,
        "new_notifications_count": ContactMessage.objects.filter(is_read=False).count(),
    })

@admin_required
@require_POST
def contact_message_mark_read(request):
    msg_id = request.POST.get("msg_id")
    if not msg_id:
        return JsonResponse({"success": False, "error": "ID manquant"})
    try:
        msg = ContactMessage.objects.get(id=msg_id)
        msg.is_read = True
        msg.save()
        # retourne le nombre de messages non lus pour le badge
        new_count = ContactMessage.objects.filter(is_read=False).count()
        return JsonResponse({"success": True, "new_count": new_count})
    except ContactMessage.DoesNotExist:
        return JsonResponse({"success": False, "error": "Message introuvable"})
    
@admin_required
def get_new_messages_count(request):
    """Retourne le nombre de nouveaux messages non lus pour le badge."""
    count = ContactMessage.objects.filter(is_read=False).count()
    return JsonResponse({"new_messages_count": count})