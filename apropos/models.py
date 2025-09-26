from django.db import models

class Apropos(models.Model):
    titre = models.CharField(max_length=255, default="À propos de TLMT Services")
    description = models.TextField()
    image_principale = models.ImageField(upload_to='apropos/', blank=True, null=True)

    def __str__(self):
        return self.titre


class Feature(models.Model):
    apropos = models.ForeignKey(Apropos, on_delete=models.CASCADE, related_name='features')
    titre = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='apropos/features/', blank=True, null=True)

    def __str__(self):
        return self.titre


class PointCle(models.Model):
    apropos = models.ForeignKey(Apropos, on_delete=models.CASCADE, related_name='points_cles')
    texte = models.CharField(max_length=255)

    def __str__(self):
        return self.texte
