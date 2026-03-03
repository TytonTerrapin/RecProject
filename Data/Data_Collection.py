import os
import requests
import pandas as pd
import time
from tqdm import tqdm
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
if API_KEY is None:
    raise ValueError("TMDB_API_KEY not found in environment variables")

BASE_URL = "https://api.themoviedb.org/3"
TOTAL_PAGES = 50  # 50 pages × 20 movies = 1000 movies


def create_session_with_retries():
    """Create a requests session with automatic retry logic."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,  # exponential backoff: 1, 2, 4, 8, 16 seconds
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def get_movies_from_discover(page, session):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "sort_by": "popularity.desc",
        "page": page
    }
    response = session.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_movie_details(movie_id, session):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY}
    response = session.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_movie_credits(movie_id, session):
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": API_KEY}
    response = session.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_movie_keywords(movie_id, session):
    url = f"{BASE_URL}/movie/{movie_id}/keywords"
    params = {"api_key": API_KEY}
    response = session.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def extract_director(crew):
    for member in crew:
        if member["job"] == "Director":
            return member["name"]
    return None


def extract_top_cast(cast, top_n=5):
    return [member["name"] for member in cast[:top_n]]


def extract_genres(genres):
    return [genre["name"] for genre in genres]


def extract_keywords(keywords):
    return [kw["name"] for kw in keywords]


def collect_dataset():
    all_movies = []
    session = create_session_with_retries()

    for page in tqdm(range(1, TOTAL_PAGES + 1)):
        discover_data = get_movies_from_discover(page, session)

        for movie in discover_data.get("results", []):
            movie_id = movie["id"]

            try:
                details = get_movie_details(movie_id, session)
                credits = get_movie_credits(movie_id, session)
                keywords_data = get_movie_keywords(movie_id, session)

                movie_record = {
                    "movie_id": movie_id,
                    "title": details.get("title"),
                    "overview": details.get("overview"),
                    "release_date": details.get("release_date"),
                    "popularity": details.get("popularity"),
                    "vote_average": details.get("vote_average"),
                    "vote_count": details.get("vote_count"),
                    "genres": extract_genres(details.get("genres", [])),
                    "director": extract_director(credits.get("crew", [])),
                    "cast": extract_top_cast(credits.get("cast", [])),
                    "keywords": extract_keywords(keywords_data.get("keywords", []))
                }

                all_movies.append(movie_record)

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"Error processing movie {movie_id}: {e}")
                continue

    session.close()
    return pd.DataFrame(all_movies)


if __name__ == "__main__":
    df = collect_dataset()
    df.to_csv("tmdb_movies_dataset.csv", index=False)
    print("Dataset saved as tmdb_movies_dataset.csv")