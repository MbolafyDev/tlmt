# reset_db.py
import django
import os

# ⚠️ Vérifie bien que tu charges les settings prod/dev selon ton environnement
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlmt.settings")
django.setup()

from django.apps import apps
from django.db import connection

print("⚠️ Attention : toutes les tables vont être supprimées !")

with connection.cursor() as cursor:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for model in apps.get_models():
        table = model._meta.db_table
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

print("✅ Toutes les tables ont été supprimées !")
