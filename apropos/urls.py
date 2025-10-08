from django.urls import path
from .views import apropos_view, apropos_dev

urlpatterns = [
    path("", apropos_view, name="apropos"),
    path("dev-apropos/", apropos_dev, name="apropos_dev"),
]
