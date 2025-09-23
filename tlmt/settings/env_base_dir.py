from pathlib import Path
import os
from dotenv import load_dotenv

# --- Définition du BASE_DIR global ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Chargement automatique du bon .env ---
env_file = BASE_DIR / ".env.dev"  # par défaut
if os.getenv("ENV") == "production":
    env_file = BASE_DIR / ".env.prod"

load_dotenv(dotenv_path=env_file)
