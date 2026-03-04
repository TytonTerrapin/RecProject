"""
TMDB API Integration Module
Fetches movie data from The Movie Database (TMDB) API
"""

import os
import requests
from dotenv import load_dotenv
import time
from functools import lru_cache

# Load environment variables
load_dotenv()

# Try Streamlit secrets first (for Streamlit Cloud), then fall back to environment variables
try:
    import streamlit as st
    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
except (ImportError, KeyError, FileNotFoundError):
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env file")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_POSTER_BASE = "https://image.tmdb.org/t/p/w500"

# Session for connection pooling with retry configuration
_session = None


from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_session():
    """Get or create a requests session configured with retries."""
    global _session
    if _session is None:
        session = requests.Session()
        # configure retries for transient errors
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        _session = session
    return _session


@lru_cache(maxsize=512)
def get_tmdb_movie_details(movie_id):
    """
    Fetch movie details from TMDB API.
    
    Args:
        movie_id: TMDB movie ID
    
    Returns:
        dict with: title, overview, poster_path, vote_average, vote_count, 
                  release_date, genres, cast, director, reviews
    """
    try:
        url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        params = {
            "api_key": TMDB_API_KEY,
            "append_to_response": "credits,reviews"
        }
        
        response = get_session().get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract cast (top 10)
        cast = []
        if "credits" in data and "cast" in data["credits"]:
            cast = [actor["name"] for actor in data["credits"]["cast"][:10]]
        
        # Extract director
        director = ""
        if "credits" in data and "crew" in data["credits"]:
            directors = [crew["name"] for crew in data["credits"]["crew"] if crew["job"] == "Director"]
            if directors:
                director = directors[0]
        
        # Extract reviews
        reviews = []
        if "reviews" in data and "results" in data["reviews"]:
            reviews = [
                {
                    "author": review["author"],
                    "content": review["content"],
                    "rating": review.get("author_details", {}).get("rating"),
                    "url": review["url"]
                }
                for review in data["reviews"]["results"]
            ]
        
        # Extract genres
        genres = [genre["name"] for genre in data.get("genres", [])]
        
        # Build poster path
        poster_path = ""
        if data.get("poster_path"):
            poster_path = f"{TMDB_POSTER_BASE}{data['poster_path']}"
        
        return {
            "movie_id": movie_id,
            "title": data.get("title", ""),
            "overview": data.get("overview", ""),
            "poster_path": poster_path,
            "poster_path_relative": data.get("poster_path", ""),  # Relative path for potential use
            "vote_average": data.get("vote_average", 0),
            "vote_count": data.get("vote_count", 0),
            "release_date": data.get("release_date", ""),
            "genres": genres,
            "cast": cast,
            "director": director,
            "reviews": reviews,
            "budget": data.get("budget", 0),
            "revenue": data.get("revenue", 0),
            "runtime": data.get("runtime", 0),
            "status": data.get("status", ""),
            "popularity": data.get("popularity", 0)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching TMDB data for movie {movie_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching TMDB data for movie {movie_id}: {e}")
        return None


def search_tmdb_movies(query, limit=20):
    """
    Search for movies on TMDB.
    
    Args:
        query: Search query string
        limit: Number of results to return
    
    Returns:
        List of movies with basic info
    """
    try:
        url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "page": 1
        }
        
        response = get_session().get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for movie in data.get("results", [])[:limit]:
            poster_path = ""
            if movie.get("poster_path"):
                poster_path = f"{TMDB_POSTER_BASE}{movie['poster_path']}"
            
            results.append({
                "movie_id": movie["id"],
                "title": movie.get("title", ""),
                "overview": movie.get("overview", ""),
                "poster_path": poster_path,
                "vote_average": movie.get("vote_average", 0),
                "release_date": movie.get("release_date", ""),
                "popularity": movie.get("popularity", 0)
            })
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error searching TMDB: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error searching TMDB: {e}")
        return []


def get_tmdb_trending_movies(limit=20):
    """
    Get trending movies from TMDB.
    
    Args:
        limit: Number of results
    
    Returns:
        List of trending movies
    """
    try:
        url = f"{TMDB_BASE_URL}/trending/movie/week"
        params = {
            "api_key": TMDB_API_KEY
        }
        
        response = get_session().get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for movie in data.get("results", [])[:limit]:
            poster_path = ""
            if movie.get("poster_path"):
                poster_path = f"{TMDB_POSTER_BASE}{movie['poster_path']}"
            
            results.append({
                "movie_id": movie["id"],
                "title": movie.get("title", ""),
                "overview": movie.get("overview", ""),
                "poster_path": poster_path,
                "vote_average": movie.get("vote_average", 0),
                "release_date": movie.get("release_date", ""),
                "popularity": movie.get("popularity", 0)
            })
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trending movies from TMDB: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching trending movies: {e}")
        return []


def clear_tmdb_cache():
    """Clear the TMDB details cache."""
    get_tmdb_movie_details.cache_clear()
    print("TMDB cache cleared")
