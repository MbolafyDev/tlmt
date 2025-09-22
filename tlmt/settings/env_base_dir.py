from pathlib import Path
import os
from dotenv import load_dotenv

# --- Chargement automatique du bon .env ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_type = os.getenv("ENV", "dev")  # par défaut = dev
if env_type == "production":
    load_dotenv(BASE_DIR / ".env.prod")
else:
    load_dotenv(BASE_DIR / ".env.dev")
