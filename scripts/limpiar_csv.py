import pandas as pd
import re
from transformers import pipeline

# 1) Carga y parseo inicial
df = pd.read_csv('data/apagon_dataset_last_year.csv', parse_dates=['fecha'])

# 2) Elimina duplicados por URI
df = df.drop_duplicates(subset='uri')

# 3) Filtra posts demasiado cortos (menos de 20 caracteres)
df = df[df['texto'].str.len() >= 20]

# 4) Filtra posts sin contenido alfabético (solo URLs o caracteres especiales)
df = df[df['texto'].str.contains(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]')]

# 5) Añade columnas de metadatos
df['n_palabras'] = df['texto'].str.split().str.len()
df['has_url'] = df['texto'].str.contains(r'https?://')
df['hashtags'] = df['texto'].str.findall(r'#\w+')
df['mentions'] = df['texto'].str.findall(r'@\w+')

# 6) Analiza sentimiento
sentiment = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)
df['sentiment'] = df['texto'].apply(
    lambda txt: sentiment(txt[:512])[0]['label']
)

# 7) Guarda el CSV curado con sentimiento
df.to_csv('data/apagon_curado.csv', index=False, encoding='utf-8')

print("✅ apagon_curado.csv generado:")
print(f"   Filas originales: {len(pd.read_csv('data/apagon_dataset_last_year.csv'))}")
print(f"   Filas curadas:    {len(df)}")
