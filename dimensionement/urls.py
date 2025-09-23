from django.urls import path
from . import views

urlpatterns = [
    # Formulaire client → calcule & enregistre PDF → succès
    path("demande/", views.demande_dimensionnement_view, name="demande_dimensionnement"),
    path("success/<int:pk>/", views.demande_success_view, name="demande_success"),

    # Actions PDF
    path("telecharger/<int:pk>/", views.telecharger_pdf_view, name="telecharger_pdf"),
    path("voir/<int:pk>/", views.voir_pdf_view, name="voir_pdf"),

    # (Optionnel) Vue interne de test/calcul
    path("calc/", views.dimensionnement_view, name="dimensionnement_calc"),
]
