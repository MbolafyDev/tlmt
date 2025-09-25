from django.shortcuts import render
from django.views.generic import TemplateView

class ManifestView(TemplateView):
    template_name = "pwa/manifest.json"
    content_type = "application/manifest+json"