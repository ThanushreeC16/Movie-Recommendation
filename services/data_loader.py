import pandas as pd
import os


def load_movies():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        datasets_dir = os.path.join(base_dir, "datasets")

        # Priority: xlsx (user edits) > enriched csv > base csv
        xlsx     = os.path.join(datasets_dir, "movies_updated.xlsx")
        enriched = os.path.join(datasets_dir, "movies_updated.csv")
        fallback = os.path.join(datasets_dir, "movies.csv")

        if os.path.exists(xlsx):
            movies = pd.read_excel(xlsx, dtype=str)
            source = "movies_updated.xlsx"
        elif os.path.exists(enriched):
            movies = pd.read_csv(enriched, dtype=str)
            source = "movies_updated.csv"
        else:
            movies = pd.read_csv(fallback, dtype=str)
            source = "movies.csv"

        # Drop blank rows and duplicate header rows
        movies = movies[
            movies["movie_id"].notna()
            & (movies["movie_id"].str.strip() != "")
            & (movies["movie_id"] != "movie_id")
        ]
        movies = movies.reset_index(drop=True)

        # Ensure enrichment columns exist
        for col in ("poster_url", "description", "movie_link"):
            if col not in movies.columns:
                movies[col] = ""

        movies = movies.fillna("")

        print(f"Dataset loaded: {len(movies)} movies from {source}")
        return movies

    except Exception as e:
        print("Error loading dataset:", e)
        return None
