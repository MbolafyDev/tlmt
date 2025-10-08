from django.db import models

# Create your models here.

class AppareilSanitaire(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    debit_brut = models.FloatField(help_text="Débit brut Qb en L/s")
    eau_chaude = models.BooleanField(default=False, help_text="L'appareil utilise-t-il l'eau chaude ?")
    image = models.ImageField(upload_to="appareils/", blank=True, null=True)

    def __str__(self):
        return self.nom
    
class SelectionAppareil(models.Model):
    nom_utilisateur = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    appareil = models.ForeignKey(AppareilSanitaire, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nom_utilisateur} - {self.appareil.nom}"