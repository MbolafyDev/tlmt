from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from . forms import EditProfileForm

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            current_site = get_current_site(request)
            subject = "Activation de votre compte"
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(
                reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
            )
            message = render_to_string('users/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
                'domain': current_site.domain,
            })
            send_mail(subject, message, 'noreply@monsite.com', [user.email])
            messages.success(request, 'Votre compte a été créé. Vérifiez votre email pour l’activer.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.validated_by_admin = True
        user.save()
        messages.success(request, "Votre compte est maintenant activé !")
        return redirect('login')
    else:
        messages.error(request, "Lien d'activation invalide ou expiré.")
        return redirect('register')

def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "Vous devez activer votre compte via email avant de vous connecter.")
                return redirect('login')
            auth_login(request, user)
            return redirect("home")
    else:
        form = CustomAuthenticationForm()
    return render(request, "users/login.html", {"form": form})

def logout_view(request):
    auth_logout(request)
    return redirect("home")

@login_required
def profile_view(request):
    return render(request, "users/profile.html", {"user": request.user})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'users/edit_profile.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = '/users/password-reset/done/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = '/users/password-reset/complete/'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('password_change_done')

@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'
