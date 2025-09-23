from django.contrib import admin
from .models import DemandeDimensionnement

@admin.register(DemandeDimensionnement)
class DemandeDimensionnementAdmin(admin.ModelAdmin):
    list_display = ("nom", "email", "energie_journaliere", "puissance_crete", "created_at")
    search_fields = ("nom", "email")