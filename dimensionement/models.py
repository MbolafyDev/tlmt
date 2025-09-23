from django.db import models

class Dimensionnement(models.Model):
    energie_journaliere = models.FloatField(null=True, blank=True)
    coefficient_k = models.FloatField(null=True, blank=True)
    irradiation = models.FloatField(null=True, blank=True)
    puissance_totale_ac = models.FloatField(null=True, blank=True)
    jours_autonomie = models.IntegerField(null=True, blank=True)
    tension_systeme = models.FloatField(null=True, blank=True)
    decharge_max = models.FloatField(null=True, blank=True)
    puissance_crete = models.FloatField(null=True, blank=True)
    capacite_batterie = models.FloatField(null=True, blank=True)
    puissance_onduleur = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Dimensionnement {self.id}"


class DemandeDimensionnement(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)

    # Entrées calcul
    jours_autonomie = models.IntegerField(default=3)
    irradiation = models.FloatField("Irradiation (kWh/m².j)", default=2.4)
    rendement_k = models.FloatField("Coefficient K", default=0.65)

    # (Compat) ancien champ texte "appareils"
    appareils = models.TextField(blank=True, null=True)

    # Résultats "internes" (non affichés)
    energie_journaliere = models.FloatField(null=True, blank=True)
    puissance_crete = models.FloatField(null=True, blank=True)
    tension_systeme = models.FloatField(null=True, blank=True)
    capacite_batterie = models.FloatField(null=True, blank=True)
    puissance_onduleur = models.FloatField(null=True, blank=True)

    # Propositions stockées en JSON sérialisé (string) pour compat SQLite
    panneaux_propositions = models.TextField(blank=True, default="[]")
    batteries_propositions = models.TextField(blank=True, default="[]")


    # PDF
    pdf = models.FileField(upload_to="dimensionements/%Y/%m/%d/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de {self.nom} ({self.email})"
