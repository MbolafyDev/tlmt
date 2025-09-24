from django.urls import path
from .views import contact_view

urlpatterns = [
    path('contactez-nous/', contact_view, name='contact'),
]