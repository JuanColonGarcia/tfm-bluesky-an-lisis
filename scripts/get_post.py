import os
from atproto import Client, models
from dotenv import load_dotenv

# 1) Carga credenciales
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
BSY_USER = os.getenv("BSY_USER")
BSY_PASS = os.getenv("BSY_PASS")
if not (BSY_USER and BSY_PASS):
    raise RuntimeError("Define BSY_USER y BSY_PASS en .env")

# 2) Inicializa cliente
client = Client()
client.login(BSY_USER, BSY_PASS)

def get_post_by_uri(uri: str):
    """Recupera el post completo (texto, fecha, embed, etc.) dado su URI."""
    params = models.AppBskyFeedGetPost.Params(uri=uri)
    resp = client.app.bsky.feed.getPost(params=params)
    return resp.record

if __name__ == "__main__":
    uri = input("URI del post a recuperar: ")
    record = get_post_by_uri(uri)
    print(f"Texto: {record.text}")
    print(f"Fecha: {record.created_at}")
    if record.embed and getattr(record.embed, "images", None):
        thumbs = [img.thumb for img in record.embed.images]
        print("Miniaturas de imágenes:", thumbs)
