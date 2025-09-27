from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/edit/", views.edit_user, name="edit_user"),
]
