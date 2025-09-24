from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="/home"),
    path('produit/<int:produit_id>/', views.produit_detail, name='produit_detail'),
]
