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
]
