from django.urls import path
from .views import apropos_view

urlpatterns = [
    path("", apropos_view, name="apropos"),
]
