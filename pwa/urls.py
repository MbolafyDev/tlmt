from django.urls import path
from .views import ManifestView

urlpatterns = [
    path("manifest.json", ManifestView.as_view(), name="manifest"),
]
