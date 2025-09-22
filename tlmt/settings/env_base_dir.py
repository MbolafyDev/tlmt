from pathlib import Path
import os

# Détection automatique de l'environnement
ENV = os.getenv("ENV", "local")  # "production" ou "local"

# BASE_DIR dépend de l'env (ici tu peux simplifier si tu veux)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
