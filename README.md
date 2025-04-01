# 🧠 Análisis de Reddit: Brandon Sanderson y el Cosmere

Este proyecto realiza un análisis de sentimiento sobre publicaciones de Reddit relacionadas con Brandon Sanderson y sus libros del universo Cosmere.

## 🔍 ¿Qué hace este script?

- Extrae publicaciones desde los subreddits `r/books`, `r/fantasy` y `r/brandonsanderson`.
- Analiza el sentimiento de las publicaciones (positivo, negativo o neutral).
- Cuenta menciones por libro.
- Calcula porcentajes de críticas negativas y positivas por libro.
- Genera gráficas para visualizar:
  - Distribución del sentimiento por subreddit
  - Menciones de libros por subreddit
  - Porcentaje de críticas negativas y positivas por libro

## 📦 Requisitos

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## 🚀 Ejecución

Ejecuta el script principal:

```bash
python sanderson_analysis_clean.py
```

Los resultados se guardarán en la carpeta `data/`.

## 📁 Estructura del proyecto

```
sanderson-analysis/
├── sanderson_analysis_clean.py
├── requirements.txt
├── README.md
└── data/
    └── comparativa_subreddits_sanderson.csv
```

