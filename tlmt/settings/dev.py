from .base import *
from .env_base_dir import BASE_DIR

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Emails affichés dans la console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
