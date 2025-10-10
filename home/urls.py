from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('produit/<int:produit_id>/', views.produit_detail, name='produit_detail_home'),

    # Page ventes
    path('ventes/', views.ventes, name='ventes'),  # Tous les produits
    path('ventes/categorie/<slug:slug>/', views.ventes, name='ventes_categorie'),  # Par catégorie

    path('checkout/', views.checkout, name='checkout'),
    path('categorie/<slug:slug>/', views.categorie_detail, name='categorie_detail'),
    path('ajouter-au-panier/', views.ajouter_au_panier, name='ajouter_au_panier'),
]
