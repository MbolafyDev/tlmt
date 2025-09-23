from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Gestion propre du chemin SQLite si DB_NAME est fourni
_db_name_env = os.getenv("DB_NAME", "db.sqlite3")
if os.path.isabs(_db_name_env):
    _db_name = _db_name_env
else:
    _db_name = BASE_DIR / _db_name_env

DATABASES = {
    'default': {
        'ENGINE': os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        'NAME': _db_name,
    }
}

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "webmaster@localhost")
