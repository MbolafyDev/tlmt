from django.urls import path
from . import views

urlpatterns = [
    path('calcul-tuyauterie/', views.calcul_tuyauterie, name='calcul_tuyauterie'),
]
