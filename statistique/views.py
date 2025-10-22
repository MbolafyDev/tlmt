from django.shortcuts import render

# Create your views here.
# statistiques/views.py
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required
from home.models import Commande, Service
from django.contrib.auth.decorators import login_required

@staff_member_required
@login_required
def dashboard(request):
    # ----- Commandes -----
    total_commandes = Commande.objects.count()
    total_ventes = Commande.objects.aggregate(total=Sum('total'))['total'] or 0

    commandes_par_mode = Commande.objects.values('mode_paiement').annotate(total=Count('id'))

    # ----- Services -----
    total_services = Service.objects.count()
    services_planifie = Service.objects.filter(statut='planifie').count()
    services_en_cours = Service.objects.filter(statut='en_cours').count()
    services_termine = Service.objects.filter(statut='termine').count()

    context = {
        "total_commandes": total_commandes,
        "total_ventes": total_ventes,
        "commandes_par_mode": list(commandes_par_mode),
        "total_services": total_services,
        "services_planifie": services_planifie,
        "services_en_cours": services_en_cours,
        "services_termine": services_termine,
    }

    return render(request, "statistique/dashboard.html", context)
