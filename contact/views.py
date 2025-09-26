# contact/views.py
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.utils import formataddr
from django.utils.html import escape  # pour éviter toute injection HTML
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

            # Corps texte (plain text)
            text_body = (
                "Vous avez reçu un nouveau message depuis le formulaire de contact.\n\n"
                f"Nom : {contact.nom}\n"
                f"Email : {contact.email}\n"
                f"Sujet : {contact.sujet or 'Sans sujet'}\n\n"
                f"Message :\n{contact.message}\n"
            )

            # --- Sécurisation & pré-calculs pour le HTML (pas de backslash dans f-string) ---
            site_name_html = escape(site_name)
            nom_html = escape(contact.nom)
            email_client_html = escape(contact.email)
            sujet_html = escape(contact.sujet or "Sans sujet")
            # On échappe d'abord puis on remplace les retours à la ligne par <br>
            message_html = escape(contact.message).replace("\n", "<br>")

            html_body = (
                f"<h3>Nouveau message — {site_name_html}</h3>"
                f"<p><strong>Nom :</strong> {nom_html}</p>"
                f"<p><strong>Email :</strong> {email_client_html}</p>"
                f"<p><strong>Sujet :</strong> {sujet_html}</p>"
                f"<p><strong>Message :</strong><br>{message_html}</p>"
            )

            # From: adresse de ton domaine (meilleure délivrabilité) + display name parlant
            display_name = f"{contact.nom} via {site_name} ({contact.email})"
            from_email = formataddr((display_name, settings.DEFAULT_FROM_EMAIL))

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=from_email,
                to=[settings.DEFAULT_FROM_EMAIL],   # ta boîte
                reply_to=[contact.email],           # "Répondre" => client
                headers={"X-Contact-Email": contact.email},
            )
            email.attach_alternative(html_body, "text/html")
            email.send(fail_silently=False)

            success = True
            form = ContactForm()  # reset
    else:
        form = ContactForm()

    return render(request, "contact/contact.html", {"form": form, "success": success})