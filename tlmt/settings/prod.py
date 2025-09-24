from .base import *
import os

DEBUG = False

# Hosts autorisés
ALLOWED_HOSTS = [
    "tlmt.pythonanywhere.com",
    "www.tlmt.pythonanywhere.com",
]

# Ajout automatique du domaine depuis une variable d’environnement (sécurité/flexibilité)
domain = os.environ.get("PYTHONANYWHERE_DOMAIN", "tlmt.pythonanywhere.com")
if domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(domain)

# Base de données MySQL
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": os.getenv("DB_NAME", "tlmt$default"),
        "USER": os.getenv("DB_USER", "tlmt"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "tlmt.mysql.pythonanywhere-services.com"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES', NAMES 'utf8mb4'",
        },
        "CONN_MAX_AGE": 60,
    }
}

# Emails
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Sécurité
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF protection : autorise automatiquement tes domaines
CSRF_TRUSTED_ORIGINS = [
    f"https://{h}" for h in ALLOWED_HOSTS if not h.startswith("localhost")
]
