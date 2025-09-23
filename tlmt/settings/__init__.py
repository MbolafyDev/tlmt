import os
import pymysql

pymysql.install_as_MySQLdb()

from .env_base_dir import BASE_DIR

ENV = (os.getenv("ENV") or os.getenv("DJANGO_ENV") or "").lower()

if not ENV:
    ENV = "production" if os.path.exists(os.path.join(BASE_DIR, ".env.prod")) else "development"

if ENV.startswith("prod"):
    from .prod import *
    ACTIVE_SETTINGS = "prod"
else:
    from .dev import *
    ACTIVE_SETTINGS = "dev"

print(f"[settings] ENV={ENV} -> settings.{ACTIVE_SETTINGS}")
