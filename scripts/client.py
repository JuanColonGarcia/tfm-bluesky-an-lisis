# client.py
import os
from atproto import Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
BSY_USER = os.getenv("BSY_USER")
BSY_PASS = os.getenv("BSY_PASS")
if not (BSY_USER and BSY_PASS):
    raise RuntimeError("Define BSY_USER y BSY_PASS en tu .env antes de ejecutar este script.")

client = Client()
client.login(BSY_USER, BSY_PASS)   # igual que antes

post = client.send_post("Hello world! I posted this via the Python SDK.")

print("✔️  Post creado:")
print("    URI:", post.uri)
print("    CID:", post.cid)
