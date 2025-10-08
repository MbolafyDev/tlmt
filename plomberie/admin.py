from django.contrib import admin
from .models import AppareilSanitaire

# Register your models here.
@admin.register(AppareilSanitaire)
class AppareilSanitaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'debit_brut', 'eau_chaude', 'image_preview')
    search_fields = ('nom',)
    list_filter = ('eau_chaude',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" style="object-fit:cover;">'
        return "Aucune image"
    image_preview.allow_tags = True
    image_preview.shor_description = "Aperçu"