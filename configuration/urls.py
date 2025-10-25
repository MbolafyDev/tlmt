from django.urls import path
from . import views

urlpatterns = [
    # ---------------- Users ----------------
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/edit/", views.edit_user, name="edit_user"),
    path("users/<int:user_id>/delete/", views.delete_user, name="delete_user"),

    # ---------------- Produits ----------------
    path("produits/", views.produit_list, name="produit_list"),
    path("produits/add/", views.produit_add, name="produit_add"),
    path("produits/<int:produit_id>/detail/", views.produit_detail, name="produit_detail"),
    path("produits/<int:produit_id>/edit/", views.produit_edit, name="produit_edit"),
    path("produits/<int:produit_id>/delete/", views.produit_delete, name="produit_delete"),

    # ---------------- Catégories ----------------
    path('categories/', views.categorie_list, name='categorie_list'),
    path('categories/add/', views.categorie_add, name='categorie_add'),
    path('categories/edit/<int:categorie_id>/', views.categorie_edit, name='categorie_edit'),
    path('categories/delete/<int:categorie_id>/', views.categorie_delete, name='categorie_delete'),

    # ---------------- Caractéristiques ----------------
    path('caracteristiques/', views.caracteristique_list, name='caracteristique_list'),
    path('caracteristiques/add/', views.caracteristique_add, name='caracteristique_add'),
    path('caracteristiques/edit/<int:caracteristique_id>/', views.caracteristique_edit, name='caracteristique_edit'),
    path('caracteristiques/delete/<int:caracteristique_id>/', views.caracteristique_delete, name='caracteristique_delete'),

    # ---------------- Appareils ----------------
    path("appareils/", views.appareil_list, name="appareil_list"),
    path("appareils/add/", views.appareil_add, name="appareil_add"),
    path("appareils/<int:appareil_id>/edit/", views.appareil_edit, name="appareil_edit"),
    path("appareils/<int:appareil_id>/delete/", views.appareil_delete, name="appareil_delete"),

    # ---------------- Services ----------------
    path('services/', views.service_list, name='service_list'),
    path('services/add/', views.service_add, name='service_add'),
    path('services/<int:service_id>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:service_id>/delete/', views.service_delete, name='service_delete'),
    path('services/<int:service_id>/detail/', views.service_detail, name='service_detail'),

    # ---------------- Journal des commandes ----------------
    path('journal-commandes/', views.journal_commandes, name='journal_commandes'),

    # ... tes autres routes ...
    path('contact-messages/', views.contact_messages, name='contact_messages'),
    path('contact-messages/mark-read/', views.contact_message_mark_read, name='contact_message_mark_read'),
    # AJAX pour badge notifications
    path('ajax/new-messages-count/', views.get_new_messages_count, name='ajax_new_messages_count'),

    path('slides/', views.slide_list, name='slide_list'),
    path('slides/add/', views.slide_add, name='slide_add'),
    path('slides/edit/<int:slide_id>/', views.slide_edit, name='slide_edit'),
    path('slides/delete/<int:slide_id>/', views.slide_delete, name='slide_delete'),
]
