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
