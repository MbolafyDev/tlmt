from django.contrib import admin
from .models import Service, ServiceImage, Commande, CommandeItem

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ('image', 'ordre')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'lieu', 'statut', 'date_debut', 'date_fin', 'is_active')
    list_filter = ('statut', 'is_active', 'date_debut', 'date_fin')
    search_fields = ('titre', 'description', 'lieu')
    inlines = [ServiceImageInline]

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'user', 'total', 'email', 'date_creation')
    search_fields = ('numero_facture', 'user__username', 'email')

@admin.register(CommandeItem)
class CommandeItemAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite', 'prix_unitaire')