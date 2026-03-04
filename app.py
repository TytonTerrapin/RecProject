import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import os

# ============================================================
# Configuration
# ============================================================

# Get API URL from Streamlit secrets (Cloud) or environment variables (local)
try:
    API_BASE_URL = st.secrets["API_BASE_URL"]
except (KeyError, FileNotFoundError):
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Set page config
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .movie-card {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .movie-card:hover {
            transform: scale(1.05);
        }
        .movie-title {
            font-weight: bold;
            color: #1f77b4;
            margin-top: 10px;
        }
        .star-rating {
            color: #ffc107;
            font-size: 18px;
        }
        .details-section {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# Helper Functions
# ============================================================

def display_movies_gallery(movies, key_prefix="gallery"):
    """Display movies in a gallery format."""
    cols_per_row = 5
    
    for i in range(0, len(movies), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for col_idx, movie in enumerate(movies[i:i + cols_per_row]):
            with cols[col_idx]:
                movie_id = movie.get("movie_id")
                title = movie.get("title", "")
                rating = movie.get("vote_average")  # may be None
                poster_path = movie.get("poster_path", "")
                # wrap each poster in a div for styling
                st.markdown(f"<div class=\"movie-card\">", unsafe_allow_html=True)
                display_poster(poster_path, title=title, height=300)
                st.markdown("</div>", unsafe_allow_html=True)

                # create a button underneath to avoid overlap; no deprecated flag
                if st.button(
                    key=f"movie_{key_prefix}_{movie_id}",
                    label="View Details",
                    # width controlled by column automatically
                ):
                    st.session_state.selected_movie_id = movie_id
                    st.rerun()

                # Display title and rating (handle missing vote_average)
                st.markdown(f"**{title}**")
                st.markdown(display_star_rating(rating if rating is not None else 0), unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def fetch_popular_movies(limit=20):
    """Fetch popular movies from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/movies/popular", params={"limit": limit})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch popular movies: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to API. Make sure FastAPI is running on http://127.0.0.1:8000")
        return []
    except Exception as e:
        st.error(f"Error fetching popular movies: {str(e)}")
        return []


def search_movies(query):
    """Search for movies."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/movies/search", params={"q": query, "limit": 50})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            st.warning("Please enter a valid search query")
            return []
        else:
            st.error(f"Search failed: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to API")
        return []
    except Exception as e:
        st.error(f"Error searching movies: {str(e)}")
        return []


def fetch_movie_details(movie_id):
    """Fetch detailed information about a movie."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/movies/{movie_id}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error(f"Movie not found")
            return None
        else:
            st.error(f"Failed to fetch movie details: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to API")
        return None
    except Exception as e:
        st.error(f"Error fetching movie details: {str(e)}")
        return None


def fetch_recommendations(movie_id, top_n=10):
    """Fetch recommendations for a movie."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/recommendations/{movie_id}",
            params={"top_n": top_n}
        )
        if response.status_code == 200:
            return response.json().get("recommendations", [])
        elif response.status_code == 404:
            st.warning("No recommendations available for this movie")
            return []
        else:
            st.error(f"Failed to fetch recommendations: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to API")
        return []
    except Exception as e:
        st.error(f"Error fetching recommendations: {str(e)}")
        return []


def display_poster(poster_path, title="Movie Poster", height=300):
    """Display a movie poster (supports relative or full URL)."""
    if poster_path:
        # poster_path might be a complete URL or a relative TMDB path
        if poster_path.startswith("http"):
            st.image(poster_path, caption=title)
            return
        if poster_path.startswith("/"):
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            st.image(poster_url, caption=title)
            return
    # Placeholder for missing poster
    st.markdown(f"""
        <div style='
            background-color: #e0e0e0;
            height: {height}px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            color: #999;
        '>
            No Poster Available
        </div>
    """, unsafe_allow_html=True)


def display_star_rating(rating):
    """Display a star rating."""
    try:
        stars = int(rating / 2)
    except Exception:
        return ""
    filled = "⭐" * stars
    empty = "☆" * (5 - stars)
    return f"{filled}{empty} ({rating}/10)"


def display_movie_details(movie_id):
    """Display detailed movie information and recommendations."""
    movie = fetch_movie_details(movie_id)
    
    if movie is None:
        st.error("Could not load movie details")
        return
    
    # Back button
    if st.button("← Back to Gallery"):
        if "selected_movie_id" in st.session_state:
            del st.session_state.selected_movie_id
        st.rerun()
    
    st.divider()
    
    # Movie Header with Poster
    col_poster, col_info = st.columns([1, 2])
    
    with col_poster:
        display_poster(movie["poster_path"], title=movie["title"], height=400)
    
    with col_info:
        st.title(movie["title"])
        
        # Rating and basic info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rating", f"{movie['vote_average']}/10")
        with col2:
            st.metric("Year", movie.get("release_year", "N/A"))
        with col3:
            st.metric("Popularity", f"{movie['popularity']:.1f}")
        
        # Director and Cast
        st.subheader("👥 Cast & Crew")
        if movie.get("director"):
            st.write(f"**Director:** {movie['director']}")
        if movie.get("cast"):
            cast_list = movie["cast"]
            if isinstance(cast_list, list) and cast_list:
                cast_str = ", ".join(cast_list[:5])
                if len(cast_list) > 5:
                    cast_str += f", and {len(cast_list) - 5} more"
                st.write(f"**Cast:** {cast_str}")
        
        # Genres
        if movie.get("genres"):
            genres_list = movie["genres"]
            if isinstance(genres_list, list) and genres_list:
                genres_str = " | ".join(genres_list[:5])
                st.write(f"**Genres:** {genres_str}")
    
    # Overview
    st.subheader("📝 Overview")
    st.write(movie["overview"])
    
    # Additional Details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Release Date:** {movie.get('release_date', 'N/A')}")
    with col2:
        st.markdown(f"**Total Votes:** {movie.get('vote_count', 0):,}")
    with col3:
        st.markdown(f"**Popularity Score:** {movie.get('popularity', 0):.2f}")
    
    # Additional movie info if available
    if movie.get("runtime"):
        st.markdown(f"**Runtime:** {movie['runtime']} minutes")
    
    if movie.get("budget", 0) > 0:
        st.markdown(f"**Budget:** ${movie['budget']:,}")
    
    if movie.get("revenue", 0) > 0:
        st.markdown(f"**Revenue:** ${movie['revenue']:,}")
    
    st.divider()
    
    # Reviews Section
    if movie.get("reviews") and len(movie["reviews"]) > 0:
        st.subheader("⭐ Reviews")
        
        for review in movie["reviews"][:5]:  # Show top 5 reviews
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{review.get('author', 'Anonymous')}**")
                with col2:
                    if review.get("rating"):
                        st.write(f"Rating: {review['rating']}/10")
                
                review_text = review.get("content", "")
                if len(review_text) > 300:
                    with st.expander("Read full review"):
                        st.write(review_text)
                else:
                    st.write(review_text)
                st.divider()
    
    st.divider()
    
    # Recommendations
    st.subheader("🎬 Similar Movies You Might Like")
    
    recommendations = fetch_recommendations(movie_id, top_n=10)
    
    if recommendations:
        display_movies_gallery(recommendations, key_prefix=f"rec_{movie_id}")
    else:
        st.info("No recommendations available for this movie")


# ============================================================
# Page Layout
# ============================================================

st.title("🎬 Movie Recommender")
st.markdown("Discover movies and get personalized recommendations!")

# if a movie has been selected, skip gallery and show details only
if "selected_movie_id" in st.session_state:
    display_movie_details(st.session_state.selected_movie_id)
    # stop further rendering (gallery/search) – details replace the page
    st.stop()

# Search Section
col1, col2 = st.columns([4, 1])
with col1:
    search_query = st.text_input(
        "🔍 Search for a movie",
        placeholder="Enter movie title...",
        label_visibility="collapsed"
    )
with col2:
    search_btn = st.button("Search")

# Search Results or Popular Movies
if search_query and search_btn:
    st.subheader(f"Search Results for '{search_query}'")
    movies = search_movies(search_query)
    
    if not movies:
        st.info("No movies found matching your search. Try another title!")
    else:
        st.write(f"Found {len(movies)} movie(s)")
        display_movies_gallery(movies, key_prefix="search")
else:
    # Display Popular Movies
    st.subheader("🎯 Popular Movies")
    popular_movies = fetch_popular_movies(limit=20)
    
    if popular_movies:
        display_movies_gallery(popular_movies, key_prefix="popular")
    else:
        st.warning("Unable to load popular movies. Please check if the API is running.")
