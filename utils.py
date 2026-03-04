import pandas as pd
import numpy as np
from recommender import HybridRecommender
from tmdb_api import get_tmdb_movie_details, search_tmdb_movies, get_tmdb_trending_movies
import os

# Global variables to cache loaded data
_df_cache = None
_recommender_cache = None
_dataset_movie_ids = None


def load_dataset():
    """Load the cleaned movie dataset."""
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv("Data/tmdb_movies_cleaned.csv")
    return _df_cache


def get_dataset_movie_ids():
    """Get set of movie IDs in the cleaned dataset for quick lookup."""
    global _dataset_movie_ids
    if _dataset_movie_ids is None:
        df = load_dataset()
        _dataset_movie_ids = set(df["movie_id"].astype(int).unique())
    return _dataset_movie_ids


def is_movie_in_dataset(movie_id):
    """Check if a movie ID exists in the cleaned dataset."""
    return int(movie_id) in get_dataset_movie_ids()


def load_recommender():
    """Load the hybrid recommender model."""
    global _recommender_cache
    if _recommender_cache is None:
        _recommender_cache = HybridRecommender(model_dir="models")
    return _recommender_cache


def get_popular_movies(limit=20):
    """Get popular movies sorted by popularity from local CSV, enhanced with TMDB data."""
    df = load_dataset()
    popular = df.nlargest(limit, "popularity")[
        ["movie_id", "title", "overview", "vote_average", "release_date"]
    ].copy()
    
    # Enrich with TMDB data
    movies_list = []
    for _, row in popular.iterrows():
        movie_id = int(row["movie_id"])
        tmdb_data = get_tmdb_movie_details(movie_id)
        
        if tmdb_data:
            # Use TMDB data if available
            movie_dict = {
                "movie_id": movie_id,
                "title": tmdb_data.get("title", row["title"]),
                "overview": tmdb_data.get("overview", row["overview"]),
                "poster_path": tmdb_data.get("poster_path", ""),
                "vote_average": tmdb_data.get("vote_average", row["vote_average"]),
                "release_date": tmdb_data.get("release_date", row["release_date"])
            }
        else:
            # Fallback to CSV data
            movie_dict = {
                "movie_id": movie_id,
                "title": row["title"],
                "overview": row["overview"],
                "poster_path": "",
                "vote_average": row["vote_average"],
                "release_date": row["release_date"]
            }
        
        movies_list.append(movie_dict)
    
    return movies_list


def search_movies(query, limit=50):
    """Search for movies using TMDB API and local CSV, filtered to only dataset movies."""
    # First try TMDB API search
    tmdb_results = search_tmdb_movies(query, limit=limit * 2)  # Get more to account for filtering
    
    # Filter TMDB results to only include movies in the cleaned dataset
    filtered_results = []
    dataset_ids = get_dataset_movie_ids()
    
    for movie in tmdb_results:
        if int(movie["movie_id"]) in dataset_ids:
            filtered_results.append(movie)
            if len(filtered_results) >= limit:
                break
    
    # If we have enough filtered TMDB results, return them
    if filtered_results:
        return filtered_results
    
    # Fallback to local CSV search
    df = load_dataset()
    query_lower = query.lower()
    local_results = df[df["title"].str.lower().str.contains(query_lower, na=False)].nlargest(limit, "popularity")[
        ["movie_id", "title", "overview", "vote_average", "release_date"]
    ].copy()
    
    # Convert to list of dicts with empty poster paths
    results_list = []
    for _, row in local_results.iterrows():
        results_list.append({
            "movie_id": int(row["movie_id"]),
            "title": row["title"],
            "overview": row["overview"],
            "poster_path": "",
            "vote_average": row["vote_average"],
            "release_date": row["release_date"]
        })
    
    return results_list


def get_movie_details(movie_id):
    """Get detailed information about a specific movie from TMDB API or local dataset."""
    # Check if movie is in the cleaned dataset
    if not is_movie_in_dataset(movie_id):
        return None
    
    # Try to get TMDB data first
    tmdb_data = get_tmdb_movie_details(movie_id)
    
    if tmdb_data:
        return tmdb_data
    
    # Fallback to local CSV data
    df = load_dataset()
    movie = df[df["movie_id"] == movie_id]
    
    if movie.empty:
        return None
    
    movie = movie.iloc[0]
    
    # Parse list fields safely
    try:
        cast = eval(movie.get("cast", "[]")) if isinstance(movie.get("cast"), str) else (movie.get("cast", []) or [])
    except:
        cast = []
    
    try:
        genres = eval(movie.get("genres", "[]")) if isinstance(movie.get("genres"), str) else (movie.get("genres", []) or [])
    except:
        genres = []
    
    return {
        "movie_id": int(movie["movie_id"]),
        "title": movie["title"],
        "overview": movie["overview"],
        "poster_path": "",
        "vote_average": float(movie["vote_average"]),
        "release_date": movie.get("release_date", ""),
        "release_year": int(movie["release_year"]) if pd.notna(movie["release_year"]) else None,
        "popularity": float(movie["popularity"]),
        "director": movie.get("director", ""),
        "cast": cast,
        "genres": genres,
        "vote_count": int(movie.get("vote_count", 0)),
        "reviews": [],
        "budget": 0,
        "revenue": 0,
        "runtime": 0,
        "status": ""
    }


def get_recommendations(movie_id, top_n=10):
    """Get recommendations for a movie with TMDB data (poster, rating, etc)."""
    recommender = load_recommender()
    try:
        recommendations = recommender.recommend_by_id(movie_id, top_n=top_n)
        
        # Enrich recommendations with TMDB poster paths and other metadata
        for rec in recommendations:
            mid = rec["movie_id"]
            tmdb_data = get_tmdb_movie_details(mid)
            if tmdb_data:
                rec["poster_path"] = tmdb_data.get("poster_path", "")
                rec["vote_average"] = tmdb_data.get("vote_average", 0.0)
                rec["overview"] = tmdb_data.get("overview", "")
                rec["release_date"] = tmdb_data.get("release_date", "")
            else:
                # fallback to local CSV values if available
                df = load_dataset()
                row = df[df["movie_id"] == mid]
                if not row.empty:
                    row = row.iloc[0]
                    rec["poster_path"] = ""
                    rec["vote_average"] = row.get("vote_average", 0.0)
                    rec["overview"] = row.get("overview", "")
                    rec["release_date"] = row.get("release_date", "")
                else:
                    rec["poster_path"] = ""
                    rec["vote_average"] = 0.0
                    rec["overview"] = ""
                    rec["release_date"] = ""
        
        return recommendations
    except ValueError:
        return []


def get_movie_by_title(title):
    """Get movie ID by title from the cleaned dataset."""
    df = load_dataset()
    title_lower = title.lower()
    movie = df[df["title"].str.lower() == title_lower]
    
    if movie.empty:
        return None
    
    movie_id = int(movie.iloc[0]["movie_id"])
    
    # Verify it exists in the dataset (redundant but safe)
    if is_movie_in_dataset(movie_id):
        return movie_id
    
    return None
