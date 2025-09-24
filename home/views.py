from django.shortcuts import render, get_object_or_404

# Create your views here.
def home(request):
    return render(request, 'home/home.html')

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