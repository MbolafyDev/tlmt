from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from users.models import CustomUser
from .forms import UserValidationForm
from common.decorators import admin_required  # <-- import ici

@admin_required
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, "configuration/user_list.html", {"users": users})

@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = UserValidationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"L’utilisateur {user.username} a été mis à jour avec succès.")
            return redirect("user_list")
    else:
        form = UserValidationForm(instance=user)
    return render(request, "configuration/edit_user.html", {"form": form, "user": user})
