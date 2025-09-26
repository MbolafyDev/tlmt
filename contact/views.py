# home/views.py
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.utils import formataddr  # pour un display name propre
from .forms import ContactForm

def contact_view(request):
    success = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()  # sauvegarde dans DB

            site_name = getattr(settings, "SITE_NAME", "Votre Site")

            # Sujet lisible
            subject = f"[{site_name}] Message de {contact.nom} : {contact.sujet or 'Sans sujet'}"

            # Corps texte
            text_body = (
                f"Vous avez reçu un nouveau message depuis le formulaire de contact.\n\n"
                f"Nom : {contact.nom}\n"
                f"Email : {contact.email}\n"
                f"Sujet : {contact.sujet or 'Sans sujet'}\n\n"
                f"Message :\n{contact.message}\n"
            )

            # Corps HTML (optionnel mais utile dans Gmail)
            html_body = f"""
                <h3>Nouveau message — {site_name}</h3>
                <p><strong>Nom :</strong> {contact.nom}</p>
                <p><strong>Email :</strong> {contact.email}</p>
                <p><strong>Sujet :</strong> {contact.sujet or 'Sans sujet'}</p>
                <p><strong>Message :</strong><br>{contact.message.replace('\n', '<br>')}</p>
            """

            # From: adresse de ton domaine (évite le spam), avec un display name parlant
            # Astuce: on peut inclure l'email du client dans le display name pour qu'il soit visible dans Gmail.
            display_name = f"{contact.nom} via {site_name} ({contact.email})"
            from_email = formataddr((display_name, settings.DEFAULT_FROM_EMAIL))

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=from_email,
                to=[settings.DEFAULT_FROM_EMAIL],        # ta boîte de réception
                reply_to=[contact.email],                 # répondre ira au client ✅
                headers={"X-Contact-Email": contact.email}
            )
            email.attach_alternative(html_body, "text/html")
            email.send(fail_silently=False)

            success = True
            form = ContactForm()  # reset formulaire après envoi
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form, 'success': success})
