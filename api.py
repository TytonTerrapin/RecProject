from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from utils import (
    get_popular_movies,
    search_movies,
    get_movie_details,
    get_recommendations,
    get_movie_by_title,
)

app = FastAPI(
    title="Movie Recommender API",
    description="API for getting movie recommendations using hybrid recommendation system",
    version="1.0.0"
)

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Pydantic Models
# ============================================================

class MovieBasic(BaseModel):
    movie_id: int
    title: str
    overview: str
    poster_path: str
    vote_average: float
    release_date: str


class MovieDetails(BaseModel):
    movie_id: int
    title: str
    overview: str
    poster_path: str
    vote_average: float
    release_date: str
    release_year: Optional[int] = None
    popularity: float
    director: str
    cast: List[str]
    genres: List[str]
    vote_count: int
    reviews: List[dict] = []
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: Optional[str] = None


class RecommendationItem(BaseModel):
    movie_id: int
    title: str
    score: float
    poster_path: Optional[str] = None
    vote_average: Optional[float] = None


class RecommendationResponse(BaseModel):
    movie_id: int
    title: str
    recommendations: List[RecommendationItem]


# ============================================================
# API Endpoints
# ============================================================

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Movie Recommender API is running",
        "version": "1.0.0"
    }


@app.get("/api/movies/popular", response_model=List[MovieBasic], tags=["Movies"])
async def get_popular(limit: int = Query(20, ge=1, le=100)):
    """
    Get popular movies.
    
    - **limit**: Number of movies to return (default: 20, max: 100)
    """
    movies = get_popular_movies(limit=limit)
    return movies


@app.get("/api/movies/search", response_model=List[MovieBasic], tags=["Movies"])
async def search_movie(q: str = Query(..., min_length=1), limit: int = Query(50, ge=1, le=100)):
    """
    Search for movies by title.
    
    - **q**: Search query (required)
    - **limit**: Number of results to return (default: 50, max: 100)
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    movies = search_movies(q, limit=limit)
    return movies


@app.get("/api/movies/{movie_id}", response_model=MovieDetails, tags=["Movies"])
async def get_movie(movie_id: int):
    """
    Get detailed information about a specific movie.
    
    - **movie_id**: The TMDB movie ID
    """
    movie = get_movie_details(movie_id)
    
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    
    return movie


@app.get("/api/recommendations/{movie_id}", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_movie_recommendations(
    movie_id: int,
    top_n: int = Query(10, ge=1, le=50)
):
    """
    Get recommendations for a specific movie.
    
    - **movie_id**: The TMDB movie ID
    - **top_n**: Number of recommendations to return (default: 10, max: 50)
    """
    # Verify movie exists
    movie = get_movie_details(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    
    recommendations = get_recommendations(movie_id, top_n=top_n)
    
    return {
        "movie_id": movie_id,
        "title": movie["title"],
        "recommendations": recommendations
    }


@app.post("/api/recommendations/by-title", response_model=RecommendationResponse, tags=["Recommendations"])
async def recommend_by_title(
    title: str = Query(..., min_length=1),
    top_n: int = Query(10, ge=1, le=50)
):
    """
    Get recommendations for a movie by title.
    
    - **title**: Movie title (required)
    - **top_n**: Number of recommendations to return (default: 10, max: 50)
    """
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    movie_id = get_movie_by_title(title)
    if movie_id is None:
        raise HTTPException(status_code=404, detail=f"Movie with title '{title}' not found")
    
    movie = get_movie_details(movie_id)
    recommendations = get_recommendations(movie_id, top_n=top_n)
    
    return {
        "movie_id": movie_id,
        "title": movie["title"],
        "recommendations": recommendations
    }


# ============================================================
# Error Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
