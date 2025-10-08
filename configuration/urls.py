from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/edit/", views.edit_user, name="edit_user"),

    path("produits/", views.produit_list, name="produit_list"),
    path("produits/add/", views.produit_add, name="produit_add"),
    path("produits/<int:produit_id>/detail/", views.produit_detail, name="produit_detail"),
    path("produits/<int:produit_id>/edit/", views.produit_edit, name="produit_edit"),
    path("produits/<int:produit_id>/delete/", views.produit_delete, name="produit_delete"),

    path('categories/', views.categorie_list, name='categorie_list'),
    path('categories/add/', views.categorie_add, name='categorie_add'),
    path('categories/edit/<int:categorie_id>/', views.categorie_edit, name='categorie_edit'),
    path('categories/delete/<int:categorie_id>/', views.categorie_delete, name='categorie_delete'),

    # ---------------- Caractéristiques ----------------
    path('caracteristiques/', views.caracteristique_list, name='caracteristique_list'),
    path('caracteristiques/add/', views.caracteristique_add, name='caracteristique_add'),
    path('caracteristiques/edit/<int:caracteristique_id>/', views.caracteristique_edit, name='caracteristique_edit'),
    path('caracteristiques/delete/<int:caracteristique_id>/', views.caracteristique_delete, name='caracteristique_delete'),

    path("appareils/", views.appareil_list, name="appareil_list"),
    path("appareils/add/", views.appareil_add, name="appareil_add"),
    path("appareils/<int:appareil_id>/delete/", views.appareil_delete, name="appareil_delete"),
]
