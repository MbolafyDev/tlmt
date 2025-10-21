from .env_base_dir import BASE_DIR
from .base import *
import os

# ===================== DEBUG =====================
DEBUG = False
ALLOWED_HOSTS = ["tlmt.pythonanywhere.com"]

# ===================== MIDDLEWARE / STATIC =====================
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# ===================== BASE DE DONNÉES =====================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", ""),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES', NAMES 'utf8mb4'",
        },
        "CONN_MAX_AGE": 60,
    }
}

# ===================== EMAIL =====================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_SUBJECT_PREFIX = os.getenv("EMAIL_SUBJECT_PREFIX", EMAIL_SUBJECT_PREFIX)
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", str(EMAIL_TIMEOUT)))

# ===================== SÉCURITÉ HTTPS =====================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Proxy PA
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF
CSRF_TRUSTED_ORIGINS = ["https://tlmt.pythonanywhere.com"]

# Headers sécurité
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
REFERRER_POLICY = "strict-origin-when-cross-origin"

# ===================== NOTES IMPORTANTES =====================
# 1️⃣ Pour que fetch POST fonctionne en prod :
#    - Toujours utiliser HTTPS
#    - Toujours utiliser `credentials: 'include'` côté JS
#    - Récupérer le CSRF depuis le cookie, pas uniquement depuis le template
# 2️⃣ Collect static avant déploiement : python manage.py collectstatic
# 3️⃣ Vérifier que toutes les URLs fetch utilisent {% url ... %} correctement généré
