# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

BSY_USER = os.getenv("BSY_USER")
BSY_PASS = os.getenv("BSY_PASS")
