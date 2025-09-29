# settings/base.py
from .env_base_dir import BASE_DIR
import os
import stripe

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-fallback-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
LOGIN_URL = "/users/login/"
AUTH_USER_MODEL = "users.CustomUser"

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

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr"
TIME_ZONE = "Indian/Antananarivo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

APP_VERSION = "2025-09-25.1"

# ====== Ajouts utiles pour l'email ======
SITE_NAME = os.getenv("SITE_NAME", "Bike in Mada")

# Valeurs par défaut (overridées en dev/prod)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "webmaster@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = os.getenv("EMAIL_SUBJECT_PREFIX", f"[{SITE_NAME}] ")
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "30"))  # évite les blocages SMTP

STRIPE_PUBLIC_KEY = "pk_test_51SC1qGP5LifJlFLw6Pp21GbFFJ1Y2DqNDxkTKpoEMmKlUdh4u90J46Ew9uk4KIZfSVQYMauCYrwb7s5QzrsImGZz00diJHZ3LC"
STRIPE_SECRET_KEY = "sk_test_51SC1qGP5LifJlFLwLYWh2zXZdsRhVkwSI9t996LP4PVB9m71WY2iXXuJTU4J1c6ZpZ1JBFVjlDjaYLn33W2vqudX00zEtnh4xG"

stripe.api_key = STRIPE_SECRET_KEY
