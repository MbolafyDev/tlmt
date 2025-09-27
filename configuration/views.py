from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from users.models import CustomUser
from .forms import UserValidationForm, ProduitForm, ProduitImageForm
from common.decorators import admin_required
from article.models import Produit, ProduitImage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    """
    Liste paginée des produits (12 par page).
    IMPORTANT : on passe 'produits' = objet Page, pour matcher ton paginator.html.
    """
    qs = (
        Produit.objects
        .all()
        .prefetch_related("images")
        .order_by("-id")
    )
    paginator = Paginator(qs, 12)
    page = request.GET.get("page", 1)
    try:
        produits = paginator.page(page)   # ← objet Page attendu par ton paginator.html
    except PageNotAnInteger:
        produits = paginator.page(1)
    except EmptyPage:
        produits = paginator.page(paginator.num_pages)

    return render(request, "configuration/produit_list.html", {
        "produits": produits,            # ← objet Page
        "is_paginated": paginator.num_pages > 1,
    })

@admin_required
def produit_add(request):
    if request.method == "POST":
        form = ProduitForm(request.POST)
        files = request.FILES.getlist('images')
        if form.is_valid():
            produit = form.save()
            for f in files:
                ProduitImage.objects.create(produit=produit, image=f)
            messages.success(request, f"Produit '{produit.nom}' ajouté avec succès.")
            return redirect("produit_list")
    else:
        form = ProduitForm()
    return render(request, "configuration/produit_form.html", {"form": form, "title": "Ajouter un produit"})

@admin_required
def produit_edit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        files = request.FILES.getlist('images')
        if form.is_valid():
            form.save()
            for f in files:
                ProduitImage.objects.create(produit=produit, image=f)
            messages.success(request, f"Produit '{produit.nom}' mis à jour avec succès.")
            return redirect("produit_list")
    else:
        form = ProduitForm(instance=produit)
    return render(request, "configuration/produit_form.html", {"form": form, "title": f"Modifier le produit : {produit.nom}"})

@admin_required
def produit_delete(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produit.delete()
    messages.success(request, f"Produit '{produit.nom}' supprimé avec succès.")
    return redirect("produit_list")

@admin_required
def produit_detail(request, produit_id):
    produit = get_object_or_404(
        Produit.objects.prefetch_related("images"),
        id=produit_id
    )

    # On réutilise ton formulaire pour lister TOUTES les infos visibles en "edit"
    form = ProduitForm(instance=produit)

    # On construit une liste (label, value) propre, human-readable
    details = []
    for name, field in form.fields.items():
        label = field.label or name.replace('_', ' ').title()

        # Valeur lisible: prioriser le get_FOO_display() si choices
        display_getter = f"get_{name}_display"
        if hasattr(produit, display_getter):
            value = getattr(produit, display_getter)()
        else:
            attr = getattr(produit, name, None)
            if hasattr(attr, "all"):  # ManyToMany
                value = ", ".join(str(x) for x in attr.all())
            else:
                value = attr

        # Mise en forme de base pour None / vide
        if value is None or value == "":
            value = "—"

        details.append((label, value))

    # Tu peux ajouter des champs "meta" non inclus dans le formulaire si ton modèle en a :
    for meta_field in ("created_at", "updated_at", "date_creation", "date_modification"):
        if hasattr(produit, meta_field):
            val = getattr(produit, meta_field)
            if val:
                details.append((meta_field.replace('_', ' ').title(), val))

    return render(
        request,
        "configuration/includes/produit_detail_modal.html",
        {
            "produit": produit,
            "details": details,  # ← on passe la liste des paires (label, value)
        }
    )