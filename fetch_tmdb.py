"""
One-time script to enrich movies.csv with TMDb poster, description, and movie link.

Usage:
    pip install pandas requests
    python fetch_tmdb.py

Set your TMDb API key below or in a TMDB_API_KEY environment variable.
"""

import os
import time
import pandas as pd
import requests

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
API_KEY = os.getenv("TMDB_API_KEY", "YOUR_TMDB_API_KEY")
SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"
MOVIE_BASE = "https://www.themoviedb.org/movie"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, "datasets", "movies.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "datasets", "movies_updated.csv")

# ------------------------------------------------------------------
# Load dataset — skip blank / header-repeat rows
# ------------------------------------------------------------------
df = pd.read_csv(INPUT_CSV, dtype=str)
df = df[df["movie_id"].notna() & (df["movie_id"].str.strip() != "") & (df["movie_id"] != "movie_id")]
df = df.reset_index(drop=True)

# Initialise new columns (keep existing values if re-running)
for col in ("poster_url", "description", "movie_link"):
    if col not in df.columns:
        df[col] = ""
    else:
        df[col] = df[col].fillna("")


# ------------------------------------------------------------------
# Fetch helper
# ------------------------------------------------------------------
def get_movie_details(movie_name: str, year: str = None):
    params = {"api_key": API_KEY, "query": movie_name}
    if year and str(year).strip().isdigit():
        params["year"] = int(year)

    try:
        resp = requests.get(SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            # Retry without year constraint
            if "year" in params:
                del params["year"]
                resp = requests.get(SEARCH_URL, params=params, timeout=10)
                data = resp.json()
                results = data.get("results", [])

        if results:
            movie = results[0]
            poster_path = movie.get("poster_path") or ""
            description = movie.get("overview") or ""
            movie_id = movie.get("id")

            poster_url = f"{POSTER_BASE}{poster_path}" if poster_path else ""
            movie_link = f"{MOVIE_BASE}/{movie_id}" if movie_id else ""
            return poster_url, description, movie_link

    except Exception as exc:
        print(f"  [ERROR] {movie_name}: {exc}")

    return "", "", ""


# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------
total = len(df)
for idx, row in df.iterrows():
    movie_name = str(row.get("movie_name", "")).strip()
    year = str(row.get("year", "")).strip()

    # Skip if already fetched
    if df.at[idx, "poster_url"] and df.at[idx, "movie_link"]:
        print(f"[{idx+1}/{total}] Skipped (already fetched): {movie_name}")
        continue

    poster, desc, link = get_movie_details(movie_name, year)
    df.at[idx, "poster_url"] = poster
    df.at[idx, "description"] = desc
    df.at[idx, "movie_link"] = link

    status = "✓" if poster else "✗ (no poster)"
    print(f"[{idx+1}/{total}] {status} {movie_name}")

    time.sleep(0.25)  # stay within TMDb rate limit (40 req/10s)

# ------------------------------------------------------------------
# Save
# ------------------------------------------------------------------
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nDone! Saved to: {OUTPUT_CSV}")
