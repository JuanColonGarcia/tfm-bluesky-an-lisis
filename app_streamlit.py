import streamlit as st 
import pandas as pd
import altair as alt

# 1) Carga de datos con manejo de fechas
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['fecha'] = pd.to_datetime(df['fecha'], utc=True, errors='coerce')
    df = df.dropna(subset=['fecha'])
    df['date'] = df['fecha'].dt.date
    df['hashtags'] = df['hashtags'].apply(lambda x: eval(x) if isinstance(x, str) else [])
    df['mentions'] = df['mentions'].apply(lambda x: eval(x) if isinstance(x, str) else [])
    return df

# Carga inicial
df = load_data('data/apagon_curado.csv')

# Mapeo de sentimiento a descripción
t_sent_map = {
    "1 star": "Muy negativo",
    "2 stars": "Negativo",
    "3 stars": "Neutral o mixto",
    "4 stars": "Positivo",
    "5 stars": "Muy positivo"
}
# Mapeo descriptivo y colores
color_map = {
    "Muy negativo": "#8B0000",       # rojo muy oscuro
    "Negativo": "#FF6347",           # rojo clarito
    "Neutral o mixto": "#A9A9A9",    # gris
    "Positivo": "#90EE90",           # verde clarito
    "Muy positivo": "#006400"        # verde oscuro
}
if 'sentiment' in df.columns:
    df['sentiment_desc'] = df['sentiment'].map(t_sent_map).fillna(df['sentiment'])

# 2) Título y descripción
st.title("📊 Dashboard: Posts sobre el Apagón")
st.markdown(
    "Explora los posts de Bluesky relacionados con **apagón**: "
    "filtra por fecha, analiza volumen diario, hashtags y más."
)

# 3) Filtros en la barra lateral
st.sidebar.header("Filtros")
min_dt = df['fecha'].min().date()
max_dt = df['fecha'].max().date()
min_date = st.sidebar.date_input("Desde", min_dt)
max_date = st.sidebar.date_input("Hasta", max_dt)

# Filtro por sentimiento descriptivo
if 'sentiment_desc' in df.columns:
    opciones = sorted(df['sentiment_desc'].unique())
    seleccion = st.sidebar.multiselect(
        "Sentimiento", 
        options=opciones, 
        default=opciones
    )
else:
    seleccion = []

# Filtra usando fecha y sentimiento
df_filtered = df[
    (df['date'] >= min_date) & 
    (df['date'] <= max_date) &
    ((df['sentiment_desc'].isin(seleccion)) if 'sentiment_desc' in df.columns else True)
]

# 4) Métricas rápidas
st.subheader("Métricas rápidas")
col1, col2 = st.columns(2)
col1.metric("Posts totales", len(df_filtered))
col2.metric("Rango de fechas", f"{min_date} → {max_date}")

# 5) Serie temporal de actividad
st.subheader("Posts por día")
posts_per_day = df_filtered.groupby('date').size().rename("count").reset_index()
if not posts_per_day.empty:
    line = alt.Chart(posts_per_day).mark_line().encode(
        x='date:T',
        y='count:Q'
    )
    st.altair_chart(line, use_container_width=True)
else:
    st.write("No hay datos en el rango seleccionado.")

# 6) Top hashtags y menciones
st.subheader("Top 10 hashtags")
all_tags = [tag for tags in df_filtered['hashtags'] for tag in tags]
if all_tags:
    top_tags = pd.Series(all_tags).value_counts().head(10).reset_index()
    top_tags.columns = ['hashtag', 'count']
    bar_tags = alt.Chart(top_tags).mark_bar().encode(
        x='hashtag:N',
        y='count:Q'
    )
    st.altair_chart(bar_tags, use_container_width=True)
else:
    st.write("No hay hashtags en el rango seleccionado.")

st.subheader("Top 10 menciones")
all_ments = [m for ms in df_filtered['mentions'] for m in ms]
if all_ments:
    top_ments = pd.Series(all_ments).value_counts().head(10).reset_index()
    top_ments.columns = ['mention', 'count']
    bar_ments = alt.Chart(top_ments).mark_bar().encode(
        x='mention:N',
        y='count:Q'
    )
    st.altair_chart(bar_ments, use_container_width=True)
else:
    st.write("No hay menciones en el rango seleccionado.")

# 7) Distribución de sentimiento descriptivo
st.subheader("Distribución de sentimiento")
if 'sentiment_desc' in df_filtered.columns:
    dist_desc = df_filtered['sentiment_desc'].value_counts().reset_index()
    dist_desc.columns = ['sentiment_desc', 'count']
    # Añade columna de color a DataFrame
    dist_desc['color'] = dist_desc['sentiment_desc'].map(color_map)
    # Gráfico con color codificado directamente
    chart_sent = alt.Chart(dist_desc).mark_bar().encode(
        x=alt.X('sentiment_desc:N', title='Sentimiento'),
        y=alt.Y('count:Q', title='Conteo'),
        color=alt.Color('sentiment_desc:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values())), legend=None)
    )
    st.altair_chart(chart_sent, use_container_width=True)
else:
    st.info("No hay datos de sentimiento en el rango seleccionado.")

# 8) Tendencia de sentimiento a lo largo del tiempo (valores numéricos)
st.subheader("Tendencia de sentimiento diario")
# Mapeo inverso para obtener valor numérico
inv_map = {v: int(k.split()[0]) for k, v in t_sent_map.items()}
if 'sentiment_desc' in df_filtered.columns:
    df_filtered['sent_val'] = df_filtered['sentiment_desc'].map(inv_map)
    sentiment_ts = df_filtered.groupby('date')['sent_val'].mean().reset_index()
    if not sentiment_ts.empty:
        line_sent = alt.Chart(sentiment_ts).mark_line(color='steelblue').encode(
            x='date:T',
            y='sent_val:Q'
        )
        st.altair_chart(line_sent, use_container_width=True)
    else:
        st.write("No hay datos de sentimiento por fecha en el rango seleccionado.")
else:
    st.write("No hay datos de sentimiento por fecha en el rango seleccionado.")

# 9) Tabla de posts
st.subheader("Tabla de posts filtrados")
cols_to_show = ['fecha', 'texto', 'n_palabras', 'has_url']
if 'sentiment_desc' in df_filtered.columns:
    cols_to_show.append('sentiment_desc')
st.dataframe(
    df_filtered[cols_to_show]
    .sort_values('fecha', ascending=False)
)
