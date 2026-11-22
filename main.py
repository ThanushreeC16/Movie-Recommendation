import re

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from rapidfuzz import fuzz

try:
    from .services.data_loader import load_movies
    from .services.recommendation_engine import recommend_by_movie
except ImportError:
    from services.data_loader import load_movies
    from services.recommendation_engine import recommend_by_movie
    
try:
    from .routes.recommendations import router as recommendations_router
except ImportError:
    try:
        from routes.recommendations import router as recommendations_router
    except Exception:
        recommendations_router = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers (if available)
if 'recommendations_router' in globals() and recommendations_router is not None:
    app.include_router(recommendations_router)

movies = load_movies()

# Columns returned to the frontend
RETURN_COLUMNS = [
    "movie_id",
    "movie_name",
    "language",
    "year",
    "genre",
    "actor",
    "director",
    "rating",
    "keywords",
    "poster_url",
    "description",
    "movie_link",
]


@app.get("/")
def home():
    return {"message": "Backend is running successfully"}


@app.get("/search")
def search_movies(query: str = Query(..., min_length=1)):
    if movies is None:
        return {"movies": []}

    query_text = query.strip().lower()
    raw_terms = [t for t in re.findall(r"[\w.]+", query_text) if t]

    # Detect 'top N' / 'best N' intent
    limit = None
    if "top" in raw_terms or "best" in raw_terms:
        for t in raw_terms:
            if t.isdigit():
                try:
                    limit = int(t)
                except Exception:
                    pass
                break

    stopwords = {
        "movie", "movies", "top", "best", "list", "the", "a", "an",
        "and", "or", "of", "in", "on", "by", "for", "with",
        "show", "find", "search", "give", "me", "all",
    }
    terms = [t for t in raw_terms if t not in stopwords] or raw_terms

    # Fuzzy-enabled columns (typo tolerance for names/genres/director/language/keywords)
    fuzzy_columns = ["movie_name", "actor", "genre", "keywords", "director", "language"]
    # Exact-only columns (only year and rating remain exact to keep numeric and date matches strict)
    exact_columns = ["year", "rating"]

    all_search_cols = fuzzy_columns + exact_columns
    valid_fuzzy = [c for c in fuzzy_columns if c in movies.columns]
    valid_exact = [c for c in exact_columns if c in movies.columns]
    valid_all   = [c for c in all_search_cols if c in movies.columns]

    if not valid_all:
        return {"movies": []}

    # Pre-build lowercase lists for fast access
    col_vals = {col: movies[col].fillna("").astype(str).str.lower().tolist() for col in valid_all}

    FUZZY_THRESHOLD = 82   # higher = stricter, avoids false positives

    def term_matches(term, idx, strict=True):
        # 1. Word-boundary exact match across ALL columns (handles "yash", "kant" etc.)
        for col in valid_all:
            val = col_vals[col][idx]
            if re.search(rf"\b{re.escape(term)}\b", val):
                return True

        # 2. Partial substring on movie_name only (handles "kant" -> "kantara")
        if "movie_name" in col_vals:
            if term in col_vals["movie_name"][idx]:
                return True

        # 3. Fuzzy typo matching — only for terms >= 5 chars to avoid false positives
        if len(term) < 5:
            return False

        for col in valid_fuzzy:
            val = col_vals[col][idx]
            if not val:
                continue
            # Movie title fuzzy matching: use strict rules first, and allow a relaxed fallback
            if col == "movie_name":
                if strict:
                    # strict: require very close match to avoid false positives
                    if fuzz.ratio(term, val) >= 90 or fuzz.partial_ratio(term, val) >= 90:
                        return True
                else:
                    # relaxed fallback: accept WRatio near the general fuzzy threshold
                    if fuzz.WRatio(term, val) >= FUZZY_THRESHOLD:
                        return True
                continue

            # Split comma-separated values (e.g. actor list) and match each individually
            tokens = [v.strip() for v in re.split(r"[,|]", val) if v.strip()]
            for token in tokens:
                if strict:
                    if fuzz.ratio(term, token) >= 90 or fuzz.partial_ratio(term, token) >= 90:
                        return True
                else:
                    if fuzz.WRatio(term, token) >= FUZZY_THRESHOLD or fuzz.partial_ratio(term, token) >= FUZZY_THRESHOLD:
                        return True

        return False

    scores = []
    matched_indices = []
    # 1) strict pass
    for i in range(len(movies)):
        if all(term_matches(t, i, strict=True) for t in terms):
            matched_indices.append(i)
            name_score = fuzz.partial_ratio(query_text, col_vals["movie_name"][i]) if "movie_name" in col_vals else 0
            actor_score = fuzz.partial_ratio(query_text, col_vals["actor"][i]) if "actor" in col_vals else 0
            scores.append(max(name_score, actor_score))

    # 2) relaxed fallback pass when strict found nothing
    if not matched_indices:
        for i in range(len(movies)):
            if all(term_matches(t, i, strict=False) for t in terms):
                matched_indices.append(i)
                name_score = fuzz.partial_ratio(query_text, col_vals["movie_name"][i]) if "movie_name" in col_vals else 0
                actor_score = fuzz.partial_ratio(query_text, col_vals["actor"][i]) if "actor" in col_vals else 0
                scores.append(max(name_score, actor_score))

    if not matched_indices:
        return {"movies": []}

    results_df = movies.iloc[matched_indices].copy()
    results_df["_fuzzy_score"] = scores

    if "rating" in results_df.columns:
        results_df["_rating_num"] = pd.to_numeric(results_df["rating"], errors="coerce").fillna(0)
        results_df = results_df.sort_values(by=["_fuzzy_score", "_rating_num"], ascending=[False, False])
    else:
        results_df = results_df.sort_values(by="_fuzzy_score", ascending=False)

    # Remove duplicate movies with the same title so search results are cleaner.
    if "movie_name" in results_df.columns:
        results_df = results_df.drop_duplicates(subset=["movie_name"], keep="first")

    cap = limit if limit is not None else 30
    cols = [c for c in RETURN_COLUMNS if c in results_df.columns]
    return {"movies": results_df[cols].head(cap).to_dict(orient="records")}


@app.get("/recommend")
def get_recommendations(movie_name: str = Query(..., min_length=1)):
    """Return content-based similar movies for a given movie name."""
    recommended_names = recommend_by_movie(movie_name)

    if isinstance(recommended_names, dict):
        # error or not found
        return {"movies": [], "detail": recommended_names}

    if movies is None:
        return {"movies": []}

    # Look up full movie details for each recommended name
    cols = [c for c in RETURN_COLUMNS if c in movies.columns]
    results = []
    for name in recommended_names:
        match = movies[movies["movie_name"].str.lower() == name.lower()]
        if not match.empty:
            results.append(match[cols].iloc[0].to_dict())

    return {"movies": results}
