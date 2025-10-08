from django.shortcuts import render
from .models import Apropos

def apropos_view(request):
    # Récupère l’enregistrement, sinon None
    apropos = (Apropos.objects
               .prefetch_related('features', 'points_cles')
               .first())

    # Prépare des listes prêtes à boucler dans le template
    features = list(apropos.features.all()) if apropos else []
    points_cles = list(apropos.points_cles.all()) if apropos else []

    context = {
        "apropos": apropos,
        "features": features,
        "points_cles": points_cles,
    }
    return render(request, "apropos/apropos.html", context)

def apropos_dev(request):
    return render(request, 'apropos/apropos-dev.html')
