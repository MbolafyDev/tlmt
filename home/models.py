from django.db import models
from django.conf import settings
from article.models import Produit
from django.utils import timezone

# ======= Commandes =======
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


# ======= Services =======
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
    duree = models.CharField(max_length=100, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/')
    ordre = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"{self.service.titre} - Image {self.id}"


# ======= Likes =======
class ServiceLike(models.Model):
    service = models.ForeignKey(Service, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='service_likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('service', 'user')

    def __str__(self):
        return f"{self.user.username} aime {self.service.titre}"


# ======= Commentaires =======
class ServiceComment(models.Model):
    service = models.ForeignKey(Service, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='service_comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} commente {self.service.titre}"
