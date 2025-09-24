import os
import pymysql
pymysql.install_as_MySQLdb()

from .env_base_dir import BASE_DIR

# --- Détection automatique de l'environnement ---
# Priorité à la variable d'environnement ENV
ENV = (os.getenv("ENV") or os.getenv("DJANGO_ENV") or "").lower()

# Fallback : si aucune variable ENV, on détecte local vs prod selon l'existence du .env.prod
if not ENV:
    ENV = "production" if os.path.exists(os.path.join(BASE_DIR, ".env.prod")) else "development"

# Charger les settings appropriés
if ENV.startswith("prod") or ENV == "production":
    from .prod import *
    ACTIVE_SETTINGS = "prod"
else:
    from .dev import *
    ACTIVE_SETTINGS = "dev"

print(f"[settings] ENV={ENV} -> settings.{ACTIVE_SETTINGS}")
