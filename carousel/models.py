# tlmt/carousel/models.py

from django.db import models

class Slide(models.Model):
    titre = models.CharField(max_length=200, blank=True)
    sous_titre = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='carousel/')
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return self.titre or f"Slide {self.id}"
