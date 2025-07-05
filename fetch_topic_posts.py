#!/usr/bin/env python3
import os
import sys
import csv
from datetime import datetime, timezone, timedelta
from atproto import Client, models
from dotenv import load_dotenv

def main():
    # 1) Carga credenciales
    load_dotenv()
    user = os.getenv("BSY_USER")
    pwd  = os.getenv("BSY_PASS")
    if not (user and pwd):
        raise RuntimeError("⚠️ Define BSY_USER y BSY_PASS en tu .env")
    
    # 2) Rango temporal: últimos 30 días (fijo)
    days_back = 30
    cutoff    = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    # 3) Claves a buscar
    KEYWORDS = [
        "apagón", "España", "eléctrico", "gran", "sabemos",
        "información", "renovables", "demanda", "red", "eléctrica",
        "pedro sánchez", "sara aagesen", "mario ruiz-tagle",
        "josé bogas", "red eléctrica de españa", "ree",
        "iberdrola", "endesa", "edp",
        "asociación de empresas de energía eléctrica", "aelec"
    ]
    
    # 4) Inicializa cliente
    client = Client()
    client.login(user, pwd)
    
    # 5) Prepara CSV de salida
    os.makedirs("data", exist_ok=True)
    outfile = os.path.join("data", "multi_keyword_last_30d.csv")
    writer  = csv.writer(open(outfile, "w", newline="", encoding="utf-8"))
    writer.writerow(["uri","cid","created_at","text","keyword"])
    
    seen_uris = set()
    total     = 0
    
    # 6) Para cada keyword, pagina y recoge posts nuevos
    for kw in KEYWORDS:
        print(f"🔍 Buscando posts con “{kw}”…")
        cursor = None
        while True:
            params = models.AppBskyFeedSearchPosts.Params(q=kw, limit=100, cursor=cursor)
            resp   = client.app.bsky.feed.search_posts(params=params)
            posts  = resp.posts or []
            if not posts:
                break
            
            oldest = None
            for item in posts:
                rec     = item.record
                created = datetime.fromisoformat(rec.created_at)
                if oldest is None or created < oldest:
                    oldest = created
                if created < cutoff:
                    # este post y los siguientes serán más antiguos: saltamos
                    continue
                if item.uri in seen_uris:
                    continue
                seen_uris.add(item.uri)
                text = rec.text.replace("\n"," ")
                writer.writerow([item.uri, item.cid, created.isoformat(), text, kw])
                total += 1
            
            if oldest and oldest < cutoff:
                break
            cursor = resp.cursor
            if not cursor:
                break
    
    print(f"\n✅ Guardados {total} posts en {outfile} (últimos {days_back} días)")
    print(f"   URIs únicas: {len(seen_uris)}")

if __name__ == "__main__":
    main()
