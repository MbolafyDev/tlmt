from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import slugify
from weasyprint import HTML
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .forms import DimensionnementForm, DemandeDimensionnementForm
from .models import DemandeDimensionnement, Dimensionnement
import math, os, json


# ---------- Outils ----------
def _to_float(s, default=0.0):
    try:
        return float(str(s).replace(",", ".").strip())
    except Exception:
        return default

def _energie_from_post_lists(request):
    noms = request.POST.getlist("noms_appareil[]")
    puissances = request.POST.getlist("puissances[]")
    durees = request.POST.getlist("durees[]")
    quantites = request.POST.getlist("quantites[]")

    n = max(len(puissances), len(durees), len(quantites), len(noms))
    noms += [""] * (n - len(noms))
    puissances += [""] * (n - len(puissances))
    durees += [""] * (n - len(durees))
    quantites += ["1"] * (n - len(quantites))

    total = 0.0
    details = []
    for i in range(n):
        p = _to_float(puissances[i], 0.0)
        h = _to_float(durees[i], 0.0)
        q = _to_float(quantites[i], 1.0)
        wh = p * h * q
        if p > 0 and h > 0 and q > 0:
            total += wh
            details.append({
                "nom": (noms[i] or "").strip(),
                "puissance": p,
                "duree": h,
                "quantite": q,
                "wh": wh
            })
    return total, details

def _fallback_energie_from_text(appareils_text):
    if not appareils_text:
        return 0.0, []
    total = 0.0
    details = []
    lignes = [l for l in appareils_text.split(";") if l.strip()]
    for ligne in lignes:
        try:
            parts = ligne.strip().split()
            p = _to_float(parts[1].replace("W", ""))
            h = _to_float(parts[2].replace("h", ""))
            q = 1.0
            wh = p * h * q
            if p > 0 and h > 0:
                total += wh
                details.append({"nom": parts[0], "puissance": p, "duree": h, "quantite": q, "wh": wh})
        except Exception:
            continue
    return total, details

def _tension_from_pc(pc):
    if pc <= 500:
        return 12
    if pc <= 2000:
        return 24
    if pc <= 10000:
        return 48
    return 96

def _propositions_panneaux(pc):
    """Liste [{w, qty}] pour tailles 100W → 750W."""
    tailles = [100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 650, 700, 750]
    propositions = []
    for w in tailles:
        qty = int(math.ceil((pc or 0) / w)) if w > 0 else 0
        if qty < 1:
            qty = 1
        propositions.append({"w": w, "qty": qty})
    return propositions

def _propositions_batteries(cap_ah):
    """Liste [{ah, qty}] pour 100Ah → 500Ah (100,150,200,250,300,400,500)."""
    tailles = [100, 150, 200, 250, 300, 400, 500]
    propositions = []
    for ah in tailles:
        qty = int(math.ceil((cap_ah or 0) / ah)) if ah > 0 else 0
        if qty < 1:
            qty = 1
        propositions.append({"ah": ah, "qty": qty})
    return propositions

def _render_pdf_weasyprint(request, html_string) -> bytes:
    base_url = request.build_absolute_uri("/")
    html = HTML(string=html_string, base_url=base_url)
    return html.write_pdf()


# ---------- Vue interne (optionnelle) ----------
def dimensionnement_view(request):
    result = None
    if request.method == "POST":
        form = DimensionnementForm(request.POST)
        if form.is_valid():
            dim = form.save(commit=False)
            ec_list, _ = _energie_from_post_lists(request)
            if ec_list > 0:
                dim.energie_journaliere = ec_list

            if dim.energie_journaliere and dim.coefficient_k and dim.irradiation:
                dim.puissance_crete = dim.energie_journaliere / (dim.coefficient_k * dim.irradiation)
            if dim.energie_journaliere and dim.jours_autonomie and dim.tension_systeme and dim.decharge_max:
                dim.capacite_batterie = (dim.energie_journaliere * dim.jours_autonomie) / (dim.tension_systeme * dim.decharge_max)
            if dim.puissance_totale_ac:
                dim.puissance_onduleur = dim.puissance_totale_ac * 1.5

            dim.save()
            result = dim
    else:
        form = DimensionnementForm()

    return render(request, "dimensionement/dimensionnement_form.html", {"form": form, "result": result})


# ---------- Flux client ----------
def demande_dimensionnement_view(request):
    if request.method == "POST":
        form = DemandeDimensionnementForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)

            # 1) Énergie journalière (Wh/j)
            ec_list, details = _energie_from_post_lists(request)
            if ec_list <= 0:
                ec_text, details_text = _fallback_energie_from_text(demande.appareils)
                demande.energie_journaliere = ec_text
                details = details_text
            else:
                demande.energie_journaliere = ec_list

            # 2) Calculs internes
            k = demande.rendement_k or 0.65
            hC = demande.irradiation or 2.4
            pc = (demande.energie_journaliere or 0) / (k * hC) if (k and hC and demande.energie_journaliere) else 0.0
            demande.puissance_crete = round(pc, 2)  # stocké mais non affiché

            demande.tension_systeme = _tension_from_pc(pc)

            D = 0.8
            if demande.energie_journaliere and demande.jours_autonomie and demande.tension_systeme and D:
                cap_ah = (demande.energie_journaliere * demande.jours_autonomie) / (demande.tension_systeme * D)
            else:
                cap_ah = 0.0
            demande.capacite_batterie = round(cap_ah, 2)  # stocké mais non affiché

            p_inst_total = sum(d["puissance"] * d["quantite"] for d in details) if details else 0.0
            demande.puissance_onduleur = round(p_inst_total * 1.5, 2)

            # 3) Propositions PV & batteries -> sérialisées en JSON (TextField)
            p_list = _propositions_panneaux(pc)
            b_list = _propositions_batteries(cap_ah)
            demande.panneaux_propositions = json.dumps(p_list, ensure_ascii=False)
            demande.batteries_propositions = json.dumps(b_list, ensure_ascii=False)

            # Save avant PDF pour avoir l'ID
            demande.save()

            # 4) Génération PDF (on passe aussi les listes prêtes à l'emploi)
            context = {
                "demande": demande,
                "details": details,
                "propositions_pv": p_list,
                "propositions_batt": b_list,
            }
            html_string = render_to_string("dimensionement/dimensionnement_pdf.html", context)
            pdf_bytes = _render_pdf_weasyprint(request, html_string)

            # 5) Enregistrer PDF
            safe_name = slugify(demande.nom) or "client"
            filename = f"dimensionnement_{demande.id}_{safe_name}.pdf"
            path = default_storage.save(f"dimensionements/{filename}", ContentFile(pdf_bytes))
            demande.pdf = path
            demande.save(update_fields=["pdf"])

            return redirect(reverse("demande_success", args=[demande.id]))
    else:
        form = DemandeDimensionnementForm()

    return render(request, "dimensionement/dimensionnement_form.html", {"form": form})


def demande_success_view(request, pk: int):
    demande = get_object_or_404(DemandeDimensionnement, pk=pk)
    # Dé-sérialiser pour affichage
    try:
        p_list = json.loads(demande.panneaux_propositions or "[]")
    except Exception:
        p_list = []
    try:
        b_list = json.loads(demande.batteries_propositions or "[]")
    except Exception:
        b_list = []

    return render(
        request,
        "dimensionement/dimensionnement_success.html",
        {"demande": demande, "propositions_pv": p_list, "propositions_batt": b_list},
    )


def telecharger_pdf_view(request, pk: int):
    demande = get_object_or_404(DemandeDimensionnement, pk=pk)
    if not demande.pdf:
        return HttpResponse("PDF non disponible", status=404)
    f = default_storage.open(demande.pdf.name, "rb")
    resp = HttpResponse(f.read(), content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{os.path.basename(demande.pdf.name)}"'
    return resp


def voir_pdf_view(request, pk: int):
    demande = get_object_or_404(DemandeDimensionnement, pk=pk)
    if not demande.pdf:
        return HttpResponse("PDF non disponible", status=404)
    f = default_storage.open(demande.pdf.name, "rb")
    resp = HttpResponse(f.read(), content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{os.path.basename(demande.pdf.name)}"'
    return resp
