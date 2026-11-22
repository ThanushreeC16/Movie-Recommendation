import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.data_loader import load_movies

movies = load_movies()

if movies is not None:

    # Remove duplicate movies
    movies.drop_duplicates(
        subset="movie_name",
        inplace=True
    )

    # Create tags column
    movies["tags"] = (
        movies["genre"].astype(str) + " " +
        movies["actor"].astype(str) + " " +
        movies["director"].astype(str) + " " +
        movies["language"].astype(str) + " " +
        movies["keywords"].astype(str)
    )

    # Convert text to vectors
    cv = CountVectorizer(
        max_features=5000,
        stop_words="english"
    )

    vectors = cv.fit_transform(
        movies["tags"]
    ).toarray()

    similarity = cosine_similarity(vectors)

else:
    similarity = None


# Movie Recommendation
def recommend_by_movie(movie_name):

    if movies is None:
        return {"error": "Dataset not loaded"}

    movie_name = movie_name.lower().strip()

    movie_list = movies[
        "movie_name"
    ].str.lower()

    if movie_name not in movie_list.values:
        return {"message": "Movie not found"}

    index = movies[
        movie_list == movie_name
    ].index[0]

    distances = similarity[index]

    recommended = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )

    result = []

    for i in recommended:

        movie = movies.iloc[
            i[0]
        ]["movie_name"]

        # Avoid same movie repetition
        if movie.lower() != movie_name:

            if movie not in result:
                result.append(movie)

        # Return only top 5
        if len(result) == 5:
            break

    return result


def _movie_record(row):
    return {
        "movie_id": row.get("movie_id", ""),
        "movie_name": row.get("movie_name", ""),
        "poster_url": row.get("poster_url", ""),
        "description": row.get("description", ""),
        "language": row.get("language", ""),
        "year": row.get("year", ""),
        "genre": row.get("genre", ""),
        "actor": row.get("actor", ""),
        "director": row.get("director", ""),
        "rating": row.get("rating", ""),
        "keywords": row.get("keywords", ""),
        "movie_link": row.get("movie_link", ""),
    }


# Language Recommendation
def recommend_by_language(language, limit=30):

    result = movies[
        movies["language"]
        .str.lower() ==
        language.lower()
    ].drop_duplicates(subset="movie_name")

    return [
        _movie_record(row)
        for _, row in result.head(limit).iterrows()
    ]


# Genre Recommendation
def recommend_by_genre(genre, limit=30):

    result = movies[
        movies["genre"]
        .str.lower()
        .str.contains(
            genre.lower(),
            na=False
        )
    ].drop_duplicates(subset="movie_name")

    if result.empty:
        return []

    # Return a multilingual mix so genre filters surface movies from all languages.
    langs = result["language"].fillna("Unknown").astype(str).unique().tolist()
    groups = {
        lang: result[result["language"].fillna("Unknown").astype(str) == lang]
        for lang in langs
    }
    pointers = {lang: 0 for lang in langs}
    collected = []
    seen = set()

    while len(collected) < limit:
        added = False
        for lang in langs:
            subset = groups[lang]
            idx = pointers[lang]
            if idx >= len(subset):
                continue
            row = subset.iloc[idx]
            pointers[lang] += 1
            movie_id = str(row["movie_id"])
            if movie_id in seen:
                continue
            collected.append(_movie_record(row))
            seen.add(movie_id)
            added = True
            if len(collected) >= limit:
                break
        if not added:
            break

    if len(collected) < limit:
        remaining = result[~result["movie_id"].astype(str).isin(seen)]
        for _, row in remaining.iterrows():
            collected.append(_movie_record(row))
            if len(collected) >= limit:
                break

    return collected


def _exact_word_match(series, term):
    if term is None:
        return pd.Series(False, index=series.index)

    term = str(term).strip()
    if term == "":
        return pd.Series(False, index=series.index)

    pattern = rf"\b{re.escape(term)}\b"
    return series.astype(str).str.contains(pattern, case=False, regex=True, na=False)


# Actor Recommendation
def recommend_by_actor(actor):

    mask = _exact_word_match(movies["actor"], actor)
    result = movies[mask].drop_duplicates(subset="movie_name")

    return result.head(10).to_dict(orient="records")


# Director Recommendation
def recommend_by_director(director):

    mask = _exact_word_match(movies["director"], director)
    result = movies[mask].drop_duplicates(subset="movie_name")

    return result.head(10).to_dict(orient="records")


# Mood-based Recommendation
def recommend_by_mood(mood, top_n=30):

    if movies is None:
        return {"error": "Dataset not loaded"}

    mood = str(mood).lower().strip()

    MOOD_MAP = {
        "happy": ["comedy", "family", "romance", "feel-good", "uplifting", "funny", "lighthearted", "musical"],
        "sad": ["drama", "tragic", "melancholy", "tearjerker", "heartbreak"],
        "excited": ["action", "thriller", "adventure", "fast-paced", "suspense"],
        "romantic": ["romance", "romantic", "love", "rom-com"],
        "scary": ["horror", "thriller", "scary", "supernatural"],
        "nostalgic": ["classic", "period", "nostalgia", "retro", "vintage"],
        "thoughtful": ["drama", "biography", "psychological", "indie"],
        "feelgood": ["feel-good", "uplifting", "inspiring", "heartwarming"],
        "funny": ["comedy", "funny", "satire", "stand-up"],
    }

    keywords = MOOD_MAP.get(mood)
    if not keywords:
        # allow multi-word moods like "feel good" or freeform; break into tokens
        keywords = [m.strip() for m in re.split(r"[ ,]+", mood) if m.strip()]

    # Build combined mask from tags/genre/keywords fields
    mask = pd.Series(False, index=movies.index)
    for k in keywords:
        if not k:
            continue
        pattern = re.escape(k)
        mask = mask | movies["tags"].astype(str).str.contains(pattern, case=False, na=False)
        mask = mask | movies["genre"].astype(str).str.contains(pattern, case=False, na=False)
        mask = mask | movies["keywords"].astype(str).str.contains(pattern, case=False, na=False)

    result = movies[mask].drop_duplicates(subset="movie_name")

    # If we found results, return a diversified top slice across languages
    if not result.empty:
        # Ensure we include movies from multiple languages rather than only the largest group
        langs = result["language"].fillna("Unknown").astype(str).unique().tolist()
        num_langs = max(1, len(langs))
        per_lang = max(1, (top_n + num_langs - 1) // num_langs)
        final = []
        for lang in langs:
            subset = result[result["language"].fillna("Unknown").astype(str) == lang]
            for _, r in subset[["movie_id", "movie_name", "poster_url", "description", "language"]].head(per_lang).iterrows():
                final.append(_movie_record(r))
                if len(final) >= top_n:
                    break
            if len(final) >= top_n:
                break
        # If not enough collected (e.g., few languages), pad with top results
        if len(final) < top_n:
            # Use cosine similarity over tags to find additional relevant movies from other languages
            try:
                if similarity is not None and 'cv' in globals():
                    mood_text = " ".join(keywords)
                    mood_vec = cv.transform([mood_text]).toarray()
                    sims = cosine_similarity(mood_vec, vectors)[0]
                    ranked = sorted(list(enumerate(sims)), key=lambda x: x[1], reverse=True)
                    for idx, _score in ranked:
                        m = movies.iloc[idx]
                        item = _movie_record(m)
                        if item not in final:
                            final.append(item)
                        if len(final) >= top_n:
                            break
                else:
                    for _, r in movies[["movie_id", "movie_name", "poster_url", "description", "language"]].drop_duplicates(subset="movie_name").iterrows():
                        item = _movie_record(r)
                        if item not in final:
                            final.append(item)
                        if len(final) >= top_n:
                            break
            except Exception:
                for _, r in movies[["movie_id", "movie_name", "poster_url", "description", "language"]].drop_duplicates(subset="movie_name").iterrows():
                    item = _movie_record(r)
                    if item not in final:
                        final.append(item)
                    if len(final) >= top_n:
                        break

        return final

    # Fallback: use vector similarity against the combined tags if available
    try:
        if similarity is not None and 'cv' in globals():
            mood_text = " ".join(keywords)
            mood_vec = cv.transform([mood_text]).toarray()
            sims = cosine_similarity(mood_vec, vectors)[0]
            ranked = sorted(list(enumerate(sims)), key=lambda x: x[1], reverse=True)
            results = []
            for idx, _score in ranked:
                m = movies.iloc[idx]
                if m["movie_name"] not in [r["movie_name"] for r in results]:
                    results.append(_movie_record(m))
                if len(results) >= top_n:
                    break
            return results
    except Exception:
        pass

    return []