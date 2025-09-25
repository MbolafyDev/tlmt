from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

class ManifestView(TemplateView):
    template_name = "pwa/manifest.webmanifest"
    content_type = "application/manifest+json"

def service_worker(request):
    # Pas de cache long pour le SW : on pousse les updates
    response = render(
        request,
        "pwa/service-worker.js",
        {"APP_VERSION": getattr(settings, "APP_VERSION", "0")},
        content_type="application/javascript",
    )
    response["Cache-Control"] = "no-cache"
    response["Service-Worker-Allowed"] = "/"  # scope racine
    return response

def offline(request):
    return render(request, "pwa/offline.html", status=200)
