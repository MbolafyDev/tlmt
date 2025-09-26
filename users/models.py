from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    validated_by_admin = models.BooleanField(default=False)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True, verbose_name="Contact")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    nom_complet = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nom complet")

    def __str__(self):
        return self.username
