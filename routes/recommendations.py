from fastapi import APIRouter, Query

from services.recommendation_engine import (
    recommend_by_movie,
    recommend_by_language,
    recommend_by_genre,
    recommend_by_actor,
    recommend_by_director
)
from services.recommendation_engine import recommend_by_mood

router = APIRouter()


@router.get("/movie/{movie_name}")
def get_movie_recommendation(movie_name: str):
    return {
        "recommended_movies":
        recommend_by_movie(movie_name)
    }


@router.get("/language/{language}")
def get_language_movies(language: str, limit: int = Query(30, ge=1, le=100)):
    return {
        "movies":
        recommend_by_language(language, limit=limit)
    }


@router.get("/genre/{genre}")
def get_genre_movies(genre: str, limit: int = Query(30, ge=1, le=100)):
    return {
        "movies":
        recommend_by_genre(genre, limit=limit)
    }


@router.get("/actor/{actor}")
def get_actor_movies(actor: str):
    return {
        "movies":
        recommend_by_actor(actor)
    }


@router.get("/director/{director}")
def get_director_movies(director: str):
    return {
        "movies":
        recommend_by_director(director)
    }


@router.get("/mood/{mood}")
def get_mood_movies(mood: str, limit: int = Query(30, ge=1, le=100)):
    return {
        "movies":
        recommend_by_mood(mood, top_n=limit)
    }