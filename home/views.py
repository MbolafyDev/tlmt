from django.shortcuts import render, get_object_or_404, redirect
from article.models import Produit

PANIER_EXEMPLE = [
    {
        'nom': 'Réchaud à Pétrole 5L',
        'image': 'images/4.png',
        'quantite': 1,
        'prix_original': 65000,
        'prix': 55000
    },
    {
        'nom': 'Applique murale',
        'image': 'images/_20250311_Applique murale_Zara Store.png',
        'quantite': 2,
        'prix_original': 45000,
        'prix': 40000
    }
]
# Create your views here.
def home(request):
    produits = Produit.objects.prefetch_related("images").all()[:8]
    return render(request, 'home/home.html', {"produits": produits})


def produit_detail(request, produit_id):
    # Ici on suppose que vous avez un modèle Produit
    # produit = get_object_or_404(Produit, id=produit_id)

    # Exemple statique pour démonstration
    produit = {
        'id': produit_id,
        'nom': 'Smartwatch T800 Ultra',
        'description_courte': 'Montre connectée sportive avec écran HD, compatible Android & iOS.',
        'avis': 45,
        'prix': 299000,
        'prix_original': 350000,
        'caracteristiques': [
            'Écran 2.0” HD',
            'Bluetooth 5.0',
            'Mesure fréquence cardiaque',
            'Autonomie : 5 jours',
            'Étanche IP68'
        ],
        'couleurs': ['Orange', 'Noir', 'Argent'],
        'marque': 'Zara Tech',
        'image': 'images/20250603_Smartwatch T800 Ultra_Zara Store.png',
    }

    return render(request, 'home/detail.html', {'produit': produit})

def checkout(request):
    total = sum(item['prix'] * item['quantite'] for item in PANIER_EXEMPLE)

    if request.method == "POST":
        # Ici vous pouvez traiter la commande
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        card = request.POST.get("card")
        # Logique pour enregistrer la commande ou rediriger vers confirmation
        return redirect('commande_confirmee')  # Créez cette URL si nécessaire

    context = {
        'panier': PANIER_EXEMPLE,
        'total': total
    }
    return render(request, 'home/checkout.html', context)