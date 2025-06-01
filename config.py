# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Carga explícita del .env que está al lado de este archivo
BASE_DIR = Path(__file__).parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Variables de entorno
BSY_USER = os.getenv("BSY_USER")
BSY_PASS = os.getenv("BSY_PASS")
