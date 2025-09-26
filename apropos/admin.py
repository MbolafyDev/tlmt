from django.contrib import admin
from .models import Apropos, Feature, PointCle

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1

class PointCleInline(admin.TabularInline):
    model = PointCle
    extra = 1

@admin.register(Apropos)
class AproposAdmin(admin.ModelAdmin):
    inlines = [FeatureInline, PointCleInline]
    list_display = ('titre',)

# Optionnel : si tu veux aussi les voir séparément
admin.site.register(Feature)
admin.site.register(PointCle)
