# settings/base.py
from .env_base_dir import BASE_DIR
import os
import stripe

# settings.py (tout en haut)
import hashlib as _hashlib
__orig_md5 = _hashlib.md5
def _md5_compat(*args, **kwargs):
    kwargs.pop("usedforsecurity", None)
    return __orig_md5(*args, **kwargs)
_hashlib.md5 = _md5_compat

# -----------------------------
# Charger dotenv uniquement si pas en production
# -----------------------------
if os.getenv("ENV", "local") != "production":
    from dotenv import load_dotenv
    load_dotenv()  # charge .env local automatiquement

# -----------------------------
# Clés Stripe
# -----------------------------
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")

# Configurer Stripe
stripe.api_key = STRIPE_SECRET_KEY

# -----------------------------
# Clés et debug Django
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-fallback-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
LOGIN_URL = "/users/login/"
AUTH_USER_MODEL = "users.CustomUser"

# -----------------------------
# Apps installées
# -----------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # apps perso
    "home",
    "users",
    "widget_tweaks",
    "apropos",
    "dimensionement",
    "contact",
    "article",
    "pwa",
    "configuration",
    "common",
]

# -----------------------------
# Middleware
# -----------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tlmt.urls"
WSGI_APPLICATION = "tlmt.wsgi.application"

# -----------------------------
# Templates
# -----------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "article.context_processors.categories",
            ],
        },
    },
]

# -----------------------------
# Validation des mots de passe
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------
# Internationalisation
# -----------------------------
LANGUAGE_CODE = "fr"
TIME_ZONE = "Indian/Antananarivo"
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static et media
# -----------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------
# Version app
# -----------------------------
APP_VERSION = "2025-09-25.1"

# -----------------------------
# Email (valeurs par défaut)
# -----------------------------
SITE_NAME = os.getenv("SITE_NAME", "Bike in Mada")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "webmaster@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = os.getenv("EMAIL_SUBJECT_PREFIX", f"[{SITE_NAME}] ")
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "30"))
