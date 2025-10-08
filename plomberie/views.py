# views.py
from django.shortcuts import render, redirect
from .models import AppareilSanitaire, SelectionAppareil
import math
from django.contrib.auth.decorators import login_required 

DIAMETRES_FROIDE = [16, 20, 25, 32, 40, 50, 63]
DIAMETRES_CHAUDE = [12, 16, 20, 25, 32]

def calcul_diametre(Qb_total, total_appareils):
    if total_appareils == 0:
        return 0, 0
    elif total_appareils == 1:
        Qr = Qb_total
    else:
        Y = 1 / math.sqrt(total_appareils - 1)
        Qr = Qb_total * Y
    d_calc = math.sqrt((4 * Qr * 1e-3) / (math.pi * 2.5)) * 1000
    return round(d_calc, 2), round(Qr, 3)

def arrondi_diametre(d_calc, diametres_disponibles):
    return next((d for d in diametres_disponibles if d >= d_calc), diametres_disponibles[-1])

@login_required(login_url='login')
def calcul_tuyauterie(request):
    appareils = AppareilSanitaire.objects.all()
    resultats = None

    if request.method == "POST":
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        telephone = request.POST.get("telephone")

        # Supprimer les sélections précédentes de cet utilisateur
        SelectionAppareil.objects.filter(nom_utilisateur=nom, email=email).delete()

        # Enregistrer les nouvelles sélections
        Qb_total_froide = 0
        total_appareils_froide = 0
        Qb_total_chaude = 0
        total_appareils_chaude = 0

        for a in appareils:
            qte = int(request.POST.get(f"quantites_{a.id}", 0))
            if qte > 0:
                # Sauvegarder en base
                SelectionAppareil.objects.create(
                    nom_utilisateur=nom,
                    email=email,
                    telephone=telephone,
                    appareil=a,
                    quantite=qte
                )
                # Calculs
                Qb_total_froide += a.debit_brut * qte
                total_appareils_froide += qte
                if a.eau_chaude:
                    Qb_total_chaude += a.debit_brut * qte
                    total_appareils_chaude += qte

        # Calcul des diamètres
        diam_calc_froide, Qr_froide = calcul_diametre(Qb_total_froide, total_appareils_froide)
        diam_calc_chaude, Qr_chaude = calcul_diametre(Qb_total_chaude, total_appareils_chaude)
        diam_recommande_froide = arrondi_diametre(diam_calc_froide, DIAMETRES_FROIDE)
        diam_recommande_chaude = arrondi_diametre(diam_calc_chaude, DIAMETRES_CHAUDE) if total_appareils_chaude > 0 else None

        resultats = {
            "Qb_total_froide": round(Qb_total_froide, 3),
            "Qr_froide": Qr_froide,
            "diametre_calcule_froide": diam_calc_froide,
            "diametre_recommande_froide": diam_recommande_froide,
            "Qb_total_chaude": round(Qb_total_chaude, 3),
            "Qr_chaude": Qr_chaude,
            "diametre_calcule_chaude": diam_calc_chaude,
            "diametre_recommande_chaude": diam_recommande_chaude
        }

    return render(request, "plomberie/calcul_tuyauterie.html", {"appareils": appareils, "resultats": resultats})
