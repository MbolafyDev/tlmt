#!/usr/bin/env python
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Vérifie ENV
env = os.getenv("ENV", "").lower()

if env == "production":
    env_file = BASE_DIR / ".env.prod"
else:
    env_file = BASE_DIR / ".env.dev"

# Charge le fichier .env.* si trouvé
if env_file.exists():
    load_dotenv(env_file)

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlmt.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
