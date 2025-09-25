import os

# Récupère ENV depuis les variables d’environnement
# (par défaut = "local")
env = os.getenv("ENV", "local")

print(f"🔧 Using settings environment: {env}")

if env == "production":
    from .prod import *
else:
    from .dev import *
