import os
import random

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import create_database, save_movie

load_dotenv()

app = FastAPI()
create_database()

# Fortæller FastAPI, hvor HTML-filerne ligger
templates = Jinja2Templates(directory="templates")

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

GENRES = {
    "Action": 28,
    "Eventyr": 12,
    "Animation": 16,
    "Komedie": 35,
    "Krimi": 80,
    "Dokumentar": 99,
    "Drama": 18,
    "Familie": 10751,
    "Fantasy": 14,
    "Gyser": 27,
    "Romantik": 10749,
    "Science fiction": 878,
    "Thriller": 53,
}


def get_movie(genre_id):
    response = requests.get(
        f"{BASE_URL}/discover/movie",
        params={
            "api_key": API_KEY,
            "with_genres": genre_id,
            "language": "da-DK",
            "sort_by": "popularity.desc",
            "vote_count.gte": 50,
            "vote_average.gte": 6,
        },
        timeout=10,
    )

    response.raise_for_status()

    movies = response.json()["results"]

    if not movies:
        return None

    return random.choice(movies)


@app.get("/")
def home(
    request : Request,
    genre: int | None = None,
    saved: str | None = None,
):
    movie = None

    # Kører kun, når brugeren har klikket på en genreknap
    if genre is not None:
        movie = get_movie(genre)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "genres": GENRES,
            "movie": movie,
            "saved": saved,
        },
    )


@app.post("/save-movie")
def save_movie_to_list(
    tmdb_id: int = Form(),
    title: str = Form(),
    release_date: str = Form(""),
    vote_average: float = Form(0),
    status: str = Form(),
):
    if status not in ("watch_later", "watched"):
        raise HTTPException(status_code=400, detail="Ugyldig status")
    
    movie = {
        "id": tmdb_id,
        "title": title,
        "release_date": release_date,
        "vote_average": vote_average,
    }

    save_movie(movie, status)

    return RedirectResponse(
        url=f"/?saved={status}",
        status_code=303,
    )