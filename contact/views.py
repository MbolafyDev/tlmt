# home/views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

def contact_view(request):
    success = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()  # sauvegarde dans DB
            # Envoi email
            send_mail(
                subject=f"Message de {contact.nom}: {contact.sujet}",
                message=contact.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # votre email
                fail_silently=False,
            )
            success = True
            form = ContactForm()  # reset formulaire
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form, 'success': success})
