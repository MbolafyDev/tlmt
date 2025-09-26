from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Inscription et activation
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),

    # Connexion / Déconnexion
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profil
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
     path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Mot de passe oublié / réinitialisation
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
