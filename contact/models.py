# tlmt/contact/models.py

from django.db import models

class ContactMessage(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    sujet = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom} - {self.email}"
