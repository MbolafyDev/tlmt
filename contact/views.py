# contact/views.py
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.utils import formataddr
from django.utils.html import escape  # pour éviter toute injection HTML
from .forms import ContactForm
from .models import ContactMessage

from django.http import JsonResponse

def contact_view(request):
    success = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            # ... envoi email ici comme avant ...

            success = True
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # retourne le nombre de messages non lus pour le badge
                new_count = ContactMessage.objects.filter(is_read=False).count()
                return JsonResponse({"success": True, "new_count": new_count})

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": False, "error": "Formulaire invalide."})

    form = ContactForm()  # reset pour GET
    return render(request, "contact/contact.html", {"form": form, "success": success})
