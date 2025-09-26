# pwa/urls.py
from django.urls import path
from .views import ManifestView, service_worker, offline

urlpatterns = [
    path("manifest.webmanifest", ManifestView.as_view(), name="manifest"),
    path("service-worker.js", service_worker, name="service_worker_root"),
    path("offline/", offline, name="offline_root"),  # page de secours hors-ligne
]
