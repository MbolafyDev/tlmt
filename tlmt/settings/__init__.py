"""
Sélection dynamique des settings selon ENV.
ENV est chargé depuis .env.dev / .env.prod dans env_base_dir.py
"""

import os
import pymysql

pymysql.install_as_MySQLdb()

# ⚠️ Charger d'abord les variables .env (side-effect) :
from .env_base_dir import BASE_DIR  # noqa: F401

ENV = (os.getenv("ENV") or os.getenv("DJANGO_ENV") or "").lower()

# Fallback pratique : sur PythonAnywhere, on considère prod si .env.prod existe
if not ENV:
    ENV = "production" if os.path.exists(os.path.join(BASE_DIR, ".env.prod")) else "development"

if ENV.startswith("prod"):
    from .prod import *  # noqa
    ACTIVE_SETTINGS = "prod"
else:
    from .dev import *  # noqa
    ACTIVE_SETTINGS = "dev"

print(f"[settings] ENV={ENV} -> settings.{ACTIVE_SETTINGS}")
