from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncDay, TruncMonth, TruncYear

from home.models import Commande, Service
from users.models import CustomUser

@staff_member_required
@login_required
def dashboard(request):
    # ----- Commandes -----
    total_commandes = Commande.objects.count()
    total_ventes = Commande.objects.aggregate(total=Sum('total'))['total'] or 0
    commandes_par_mode = Commande.objects.values('mode_paiement').annotate(total=Count('id'))

    commandes_par_jour = Commande.objects.annotate(day=TruncDay('date_creation')) \
        .values('day').annotate(count=Count('id')).order_by('day')
    commandes_par_jour = [{'day': d['day'].isoformat(), 'count': d['count']} for d in commandes_par_jour]

    commandes_par_mois = Commande.objects.annotate(month=TruncMonth('date_creation')) \
        .values('month').annotate(count=Count('id')).order_by('month')
    commandes_par_mois = [{'month': d['month'].isoformat(), 'count': d['count']} for d in commandes_par_mois]

    commandes_par_annee = Commande.objects.annotate(year=TruncYear('date_creation')) \
        .values('year').annotate(count=Count('id')).order_by('year')
    commandes_par_annee = [{'year': d['year'].year, 'count': d['count']} for d in commandes_par_annee]

    # ----- Services -----
    total_services = Service.objects.count()
    services_planifie = Service.objects.filter(statut='planifie').count()
    services_en_cours = Service.objects.filter(statut='en_cours').count()
    services_termine = Service.objects.filter(statut='termine').count()

    services_par_jour = Service.objects.annotate(day=TruncDay('date_creation')) \
        .values('day').annotate(count=Count('id')).order_by('day')
    services_par_jour = [{'day': d['day'].isoformat(), 'count': d['count']} for d in services_par_jour]

    services_par_mois = Service.objects.annotate(month=TruncMonth('date_creation')) \
        .values('month').annotate(count=Count('id')).order_by('month')
    services_par_mois = [{'month': d['month'].isoformat(), 'count': d['count']} for d in services_par_mois]

    services_par_annee = Service.objects.annotate(year=TruncYear('date_creation')) \
        .values('year').annotate(count=Count('id')).order_by('year')
    services_par_annee = [{'year': d['year'].year, 'count': d['count']} for d in services_par_annee]

    # ----- Utilisateurs -----
    total_users = CustomUser.objects.count()

    logins_par_jour = CustomUser.objects.filter(last_login__isnull=False) \
        .annotate(day=TruncDay('last_login')).values('day').annotate(count=Count('id')).order_by('day')
    logins_par_jour = [{'day': d['day'].isoformat(), 'count': d['count']} for d in logins_par_jour]

    logins_par_mois = CustomUser.objects.filter(last_login__isnull=False) \
        .annotate(month=TruncMonth('last_login')).values('month').annotate(count=Count('id')).order_by('month')
    logins_par_mois = [{'month': d['month'].isoformat(), 'count': d['count']} for d in logins_par_mois]

    logins_par_annee = CustomUser.objects.filter(last_login__isnull=False) \
        .annotate(year=TruncYear('last_login')).values('year').annotate(count=Count('id')).order_by('year')
    logins_par_annee = [{'year': d['year'].year, 'count': d['count']} for d in logins_par_annee]

    context = {
        "total_commandes": total_commandes,
        "total_ventes": total_ventes,
        "commandes_par_mode": list(commandes_par_mode),
        "commandes_par_jour": commandes_par_jour,
        "commandes_par_mois": commandes_par_mois,
        "commandes_par_annee": commandes_par_annee,

        "total_services": total_services,
        "services_planifie": services_planifie,
        "services_en_cours": services_en_cours,
        "services_termine": services_termine,
        "services_par_jour": services_par_jour,
        "services_par_mois": services_par_mois,
        "services_par_annee": services_par_annee,

        "total_users": total_users,
        "logins_par_jour": logins_par_jour,
        "logins_par_mois": logins_par_mois,
        "logins_par_annee": logins_par_annee,
    }

    return render(request, "statistique/dashboard.html", context)
