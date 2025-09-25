import os

# Récupère ENV depuis les variables d’environnement
env = os.getenv("ENV", "local").lower()

print(f"🔧 Using settings environment: {env}")

if env == "production":
    from .prod import *
else:
    from .dev import *
