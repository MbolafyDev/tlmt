from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('produit/<int:produit_id>/', views.produit_detail, name='produit_detail_home'),
    path('produit/<int:produit_id>/resultat/', views.produit_detail_resultat, name='produit_detail_recherche'),

    # Pages ventes
    path('ventes/', views.ventes, name='ventes'),  
    path('ventes/categorie/<slug:slug>/', views.ventes, name='ventes_categorie'),

    # Checkout & Infos client
    path('checkout/', views.checkout, name='checkout'),
    path('info-commande/', views.info_commande, name='info_commande'),

    # Catégories
    path('categorie/<slug:slug>/', views.categorie_detail, name='categorie_detail'),

    # Panier
    path('ajouter-au-panier/', views.ajouter_au_panier, name='ajouter_au_panier'),

    # Services
    path('service/voir-plus/<int:service_id>/', views.voir_plus_service, name='voir_plus_service'),
    path('service/like/', views.like_service, name='like_service'),
    path('service/comment/', views.comment_service, name='comment_service'),
    path('service/comments/<int:service_id>/', views.get_comments_service, name='get_comments_service'),
    path('service/reply/', views.reply_comment_service, name='reply_comment_service'),
]
