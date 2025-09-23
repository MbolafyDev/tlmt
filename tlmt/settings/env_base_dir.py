from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Forcer le fichier .env selon l'existence
env_file = BASE_DIR / ".env.prod" if os.path.exists(BASE_DIR / ".env.prod") else BASE_DIR / ".env.dev"

load_dotenv(dotenv_path=env_file)

# DEBUG log pour vérifier
print("ENV chargé :", os.getenv("ENV"))
print("DB_ENGINE :", os.getenv("DB_ENGINE"))
