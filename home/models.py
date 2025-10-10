from django.db import models
from django.conf import settings
from article.models import Produit

class Commande(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    numero_facture = models.CharField(max_length=20, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    email = models.EmailField()

    def __str__(self):
        return f"{self.numero_facture} - {self.user.username}"


class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, related_name='items', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"
    

class Service(models.Model):
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    lieu = models.CharField(max_length=200, blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    duree = models.CharField(max_length=100, blank=True, null=True)  # ex: "2 semaines", "3 jours"
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/')
    ordre = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"{self.service.titre} - Image {self.id}"
