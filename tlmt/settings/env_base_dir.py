from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Charge .env.prod si présent, sinon .env.dev
env_file = BASE_DIR / ".env.prod" if os.path.exists(BASE_DIR / ".env.prod") else BASE_DIR / ".env.dev"
load_dotenv(dotenv_path=env_file)

# Logs utiles (apparaissent dans la console/les logs)
print("ENV chargé :", os.getenv("ENV"))
print("DB_ENGINE :", os.getenv("DB_ENGINE"))
