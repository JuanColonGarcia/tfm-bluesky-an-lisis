import os
import csv
from datetime import datetime, timezone, timedelta
from atproto import Client, models
from dotenv import load_dotenv

# Carga las variables de entorno desde ../.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
BSY_USER = os.getenv("BSY_USER")
BSY_PASS = os.getenv("BSY_PASS")
if not (BSY_USER and BSY_PASS):
    raise RuntimeError("Define BSY_USER y BSY_PASS en tu .env antes de ejecutar este script.")

# 1) Inicializa y autentica
client = Client()
client.login(BSY_USER, BSY_PASS)

# 2) Parámetros base de búsqueda
TOPIC = "apagón"
now    = datetime.now(timezone.utc)
# Corte a hace 365 días
cutoff = now - timedelta(days=365)

# 3) Prepara CSV de salida
outfile = os.path.join(os.path.dirname(__file__), "..", "data", "apagon_dataset_last_year.csv")
with open(outfile, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["uri", "cid", "fecha", "texto"])

    # 4) Paginación con cursor
    cursor = None
    total = 0

    while True:
        params = models.AppBskyFeedSearchPosts.Params(
            q=TOPIC,
            limit=100,    # máximo permitido
            cursor=cursor
        )
        resp = client.app.bsky.feed.search_posts(params=params)
        posts = resp.posts
        if not posts:
            break

        # 5) Procesa y escribe; si los registros son muy antiguos, paramos
        oldest = None
        for item in posts:
            rec = item.record
            created = datetime.fromisoformat(rec.created_at)
            if oldest is None or created < oldest:
                oldest = created

            if created < cutoff:
                # los siguientes serán aún más antiguos, así que rompemos
                break

            text = rec.text.replace("\n", " ")
            writer.writerow([item.uri, item.cid, created.isoformat(), text])
            total += 1

        # Si el post más antiguo de esta página ya está antes de cutoff, rompemos
        if oldest and oldest < cutoff:
            break

        # Avanza el cursor
        cursor = resp.cursor
        if not cursor:
            break

print(f"✅ Volcados {total} posts de “apagón” del último año en {outfile}")
