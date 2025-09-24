from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Charger .env selon ENV (production ou développement)
env_type = os.getenv("ENV", "development")

if env_type == "production":
    env_file = BASE_DIR / ".env.prod"
else:
    env_file = BASE_DIR / ".env.dev"

load_dotenv(dotenv_path=env_file)

print(f"ENV détecté : {env_type}")
print("DB_ENGINE :", os.getenv("DB_ENGINE"))
