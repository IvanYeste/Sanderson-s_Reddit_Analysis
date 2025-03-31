"""
Análisis de sentimiento sobre publicaciones de Reddit relacionadas con Brandon Sanderson y sus libros.
"""

import praw
import pandas as pd
from datetime import datetime
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
import os

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# --------- Libros del Cosmere ---------
libros_cosmere = [
    "The Final Empire", "The Well of Ascension", "The Hero of Ages",
    "The Alloy of Law", "Shadows of Self", "The Bands of Mourning", "The Lost Metal",
    "The Way of Kings", "Words of Radiance", "Oathbringer", "Rhythm of War", "Wind and Truth",
    "Warbreaker", "Elantris", "Arcanum Unbounded", "Tress of the Emerald Sea", 
    "Yumi and the Nightmare Painter", "The Sunlit Man"
]

# --------- Funciones ---------
def extraer_posts(subreddit_name, palabras_clave, limit_por_clave=50):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for palabra in palabras_clave:
        for submission in subreddit.search(query=palabra, limit=limit_por_clave):
            contenido = f"{submission.title} {submission.selftext}"
            posts.append({
                "subreddit": subreddit_name,
                "titulo": submission.title,
                "autor": submission.author.name if submission.author else "N/A",
                "contenido": submission.selftext,
                "score": submission.score,
                "num_comentarios": submission.num_comments,
                "fecha": datetime.fromtimestamp(submission.created_utc)
            })
    df = pd.DataFrame(posts)
    return df.drop_duplicates(subset=["titulo", "contenido"])


def clasificar_sentimiento(polaridad):
    if polaridad > 0.1:
        return "positivo"
    elif polaridad < -0.1:
        return "negativo"
    else:
        return "neutral"


def contar_menciones(df, libros):
    resultados = []
    for subreddit in df["subreddit"].unique():
        df_sub = df[df["subreddit"] == subreddit]
        conteo = {libro: 0 for libro in libros}
        for _, row in df_sub.iterrows():
            texto = f"{row['titulo']} {row['contenido']}".lower()
            for libro in libros:
                conteo[libro] += texto.count(libro.lower())
        df_conteo = pd.DataFrame(conteo.items(), columns=["Libro", "Menciones"])
        df_conteo["Subreddit"] = subreddit
        resultados.append(df_conteo)
    return pd.concat(resultados)


def calcular_porcentaje_sentimiento(df, libros, tipo="positivo"):
    resultados = []
    for libro in libros:
        menciones = df[df.apply(lambda row: libro.lower() in f"{row['titulo']} {row['contenido']}".lower(), axis=1)]
        total = len(menciones)
        positivos = len(menciones[menciones["sentimiento_clasificado"] == tipo])
        if total > 0:
            porcentaje = positivos / total * 100
            resultados.append({
                "Libro": libro,
                f"Menciones totales": total,
                f"Críticas {tipo}s": positivos,
                f"Porcentaje {tipo}": porcentaje
            })
    return pd.DataFrame(resultados).sort_values(by=f"Porcentaje {tipo}", ascending=False)


# --------- Script principal ---------
if __name__ == "__main__":
    subreddits = ["brandonsanderson", "fantasy", "books"]
    dataframes = [extraer_posts(sub, libros_cosmere) for sub in subreddits]
    df_total = pd.concat(dataframes, ignore_index=True)
    df_total = df_total[df_total["contenido"].str.len() > 20].reset_index(drop=True)

    # Sentimiento
    df_total["sentimiento"] = df_total["contenido"].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    df_total["sentimiento_clasificado"] = df_total["sentimiento"].apply(clasificar_sentimiento)

    # Gráfico 1: Distribución de sentimiento
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="subreddit", y="sentimiento", data=df_total, palette="Set2")
    plt.title("Distribución de sentimiento por subreddit")
    plt.ylabel("Polaridad de sentimiento")
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.show()

    # Gráfico 2: Conteo por tipo de sentimiento
    conteo = df_total.groupby(["subreddit", "sentimiento_clasificado"]).size().unstack().fillna(0)
    conteo.plot(kind="bar", stacked=True, figsize=(10,6), colormap="Accent")
    plt.title("Comparación de sentimiento por subreddit")
    plt.ylabel("Número de publicaciones")
    plt.xticks(rotation=0)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

    # Gráfico 3: Menciones de libros
    df_menciones = contar_menciones(df_total, libros_cosmere)
    df_menciones = df_menciones[df_menciones["Menciones"] > 0]
    plt.figure(figsize=(12,7))
    sns.barplot(data=df_menciones, y="Libro", x="Menciones", hue="Subreddit", palette="Set3")
    plt.title("Menciones de libros por subreddit")
    plt.xlabel("Menciones")
    plt.ylabel("Libro")
    plt.legend(title="Subreddit")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

    # Gráfico 4: Porcentaje de críticas negativas
    df_negativos = calcular_porcentaje_sentimiento(df_total, libros_cosmere, tipo="negativo")
    print("\n📊 Porcentaje de críticas negativas por libro:")
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_negativos, y="Libro", x="Porcentaje negativo", palette="Reds_r")
    plt.title("Porcentaje de críticas negativas por libro")
    plt.xlabel("Críticas negativas (%)")
    plt.ylabel("Libro")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

    # Gráfico 5: Porcentaje de críticas positivas
    df_positivos = calcular_porcentaje_sentimiento(df_total, libros_cosmere, tipo="positivo")
    print("\n🌟 Porcentaje de críticas positivas por libro:")
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_positivos, y="Libro", x="Porcentaje positivo", palette="Greens_r")
    plt.title("Porcentaje de críticas positivas por libro")
    plt.xlabel("Críticas positivas (%)")
    plt.ylabel("Libro")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

    # Guardar resultados
    df_total.to_csv("data/comparativa_subreddits_sanderson.csv", index=False, encoding="utf-8")
    print("✅ CSV guardado en 'data/comparativa_subreddits_sanderson.csv'")
