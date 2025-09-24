import os
import socket
import pymysql
pymysql.install_as_MySQLdb()

from .env_base_dir import BASE_DIR

# Détection automatique : local ou PythonAnywhere
hostname = socket.gethostname()
if "pythonanywhere" in hostname:
    ENV = "production"
else:
    ENV = "development"

if ENV == "production":
    from .prod import *
    ACTIVE_SETTINGS = "prod"
else:
    from .dev import *
    ACTIVE_SETTINGS = "dev"

print(f"[settings] ENV={ENV} -> settings.{ACTIVE_SETTINGS}")
