import os
import requests
import streamlit as st
import time
from dotenv import load_dotenv

# -------------------------
# Load Environment
# -------------------------

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
# URL of running recommender service; defaults to localhost if not set
RECOMMENDER_API = os.getenv("RECOMMENDER_API", "http://127.0.0.1:8000")

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# -------------------------
# TMDB Helpers
# -------------------------

# use a session with retries for TMDB requests

def _create_tmdb_session():
    session = requests.Session()
    retry = requests.packages.urllib3.util.retry.Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

_tmdb_session = _create_tmdb_session()
_tmdb_cache: dict[str, list] = {}


def search_tmdb(title):
    """Search TMDB and memoize results to limit API calls."""
    if title in _tmdb_cache:
        return _tmdb_cache[title]

    url = f"{TMDB_BASE}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }
    try:
        res = _tmdb_session.get(url, params=params, timeout=5)
        res.raise_for_status()
        results = res.json().get("results", [])
        _tmdb_cache[title] = results
        # small pause to stay under rate limits when repeatedly called
        time.sleep(0.2)
        return results
    except requests.RequestException:
        # network error or TMDB unavailable
        return []


def get_movie_details(movie_id):
    url = f"{TMDB_BASE}/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY}
    try:
        res = _tmdb_session.get(url, params=params, timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.RequestException:
        return {}
def get_poster_url(path):
    if path:
        return f"{TMDB_IMAGE_BASE}{path}"
    return None


def get_movie_credits(movie_id):
    """Return credits (cast + crew) for a TMDB movie id."""
    url = f"{TMDB_BASE}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY}
    try:
        res = _tmdb_session.get(url, params=params, timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.RequestException:
        return {}


def get_movie_reviews(movie_id, max_results: int = 5):
    """Return up to `max_results` reviews for a TMDB movie id."""
    url = f"{TMDB_BASE}/movie/{movie_id}/reviews"
    params = {"api_key": TMDB_API_KEY, "page": 1}
    try:
        res = _tmdb_session.get(url, params=params, timeout=5)
        res.raise_for_status()
        results = res.json().get("results", [])
        return results[:max_results]
    except requests.RequestException:
        return []


def extract_director_from_credits(credits):
    crew = credits.get("crew", []) if credits else []
    for member in crew:
        if member.get("job") == "Director":
            return member.get("name")
    return None


def extract_top_cast_from_credits(credits, top_n: int = 5):
    cast = credits.get("cast", []) if credits else []
    return [member.get("name") for member in cast[:top_n]]


def get_popular_movies(page: int = 1):
    """Return popular movies from TMDB (first page by default)."""
    url = f"{TMDB_BASE}/movie/popular"
    params = {"api_key": TMDB_API_KEY, "page": page}
    try:
        res = _tmdb_session.get(url, params=params, timeout=5)
        res.raise_for_status()
        return res.json().get("results", [])
    except requests.RequestException:
        return []

# -------------------------
# Recommender API Helpers
# -------------------------

def get_recommendations_by_id(movie_id):
    """Query the recommender API, return empty list on failure."""
    url = f"{RECOMMENDER_API}/recommend/id/{movie_id}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()["recommendations"]
    except requests.RequestException:
        pass
    return []


def search_local_titles(query):
    """Ask the recommender API for matching titles. Empty list if API unreachable."""
    url = f"{RECOMMENDER_API}/search"
    params = {"query": query}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json()["results"]
    except requests.RequestException:
        pass
    return []

# -------------------------
# Streamlit UI
# -------------------------

# quick health check for recommender service

def _is_backend_running():
    try:
        resp = requests.get(f"{RECOMMENDER_API}/", timeout=3)
        return resp.status_code == 200
    except requests.RequestException:
        return False


st.set_page_config(layout="wide")
st.title("🎬 Movie Recommender")

# style buttons to appear as plain text (no box) so titles sit under posters cleanly
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: transparent;
        border: none;
        box-shadow: none;
        padding: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not _is_backend_running():
    st.warning(
        "Recommender backend is not reachable. "
        "Run `python api.py` in another terminal (or set RECOMMENDER_API env)."
    )

# Search Bar
# initialize session state keys
if 'search_input' not in st.session_state:
    st.session_state['search_input'] = ''
if 'selected_title' not in st.session_state:
    st.session_state['selected_title'] = None

# Pending state helpers (e.g. clearing input) applied before widget creation
# this avoids writing to search_input after the widget has been instantiated
if 'clear_search' in st.session_state:
    st.session_state['search_input'] = ''
    st.session_state.pop('clear_search', None)


# text input bound to session state; read its live value for suggestions
st.text_input("Search for a movie", key='search_input')
query = st.session_state.get('search_input', '')

# suggestions from dataset (show while typing)
# require at least 2 characters to avoid noisy queries
if query and len(query) >= 2:
    suggestions = search_local_titles(query)
    if suggestions:
        # vertical list that updates as the input changes
        for idx, title in enumerate(suggestions):
            if st.button(title, key=f"suggest_{idx}"):
                # perform TMDB lookup immediately so we can show details on first click
                tmdb_res = search_tmdb(title)
                if tmdb_res:
                    st.session_state['selected_movie_id'] = tmdb_res[0].get("id")
                st.session_state['selected_title'] = title
                # clear input next run to collapse suggestions
                st.session_state['clear_search'] = True
    else:
        st.warning("No matching titles found in dataset.")

# handle selected movie display
if st.session_state['selected_title']:
    selected_title = st.session_state['selected_title']

    # Back button to return to homepage
    if st.button("← Back to Home"):
        st.session_state['selected_title'] = None
        st.session_state['clear_search'] = True
        st.session_state.pop('selected_movie_id', None)

    # Determine movie id (prefer pre-fetched `selected_movie_id`)
    movie_id = st.session_state.get('selected_movie_id')
    if movie_id is None:
        tmdb_results = search_tmdb(selected_title)
        if not tmdb_results:
            st.error("Movie not found on TMDB.")
            movie_id = None
        else:
            movie = tmdb_results[0]
            movie_id = movie.get("id")
            st.session_state['selected_movie_id'] = movie_id

    if movie_id is not None:
        # Display Movie Info
        details = get_movie_details(movie_id)

        col1, col2 = st.columns([1, 2])

        with col1:
            poster = get_poster_url(details.get("poster_path"))
            if poster:
                st.image(poster)

        with col2:
            st.subheader(details.get("title"))
            st.write("⭐ Rating:", details.get("vote_average"))
            st.write("📅 Release:", details.get("release_date"))
            st.write(details.get("overview"))

            # Credits (director + top cast)
            credits = get_movie_credits(movie_id)
            director = extract_director_from_credits(credits)
            top_cast = extract_top_cast_from_credits(credits, top_n=5)

            if director:
                st.markdown(f"**Director:** {director}")
            if top_cast:
                st.markdown("**Top Cast:** " + ", ".join(top_cast))

            # Reviews (short list)
            reviews = get_movie_reviews(movie_id, max_results=5)
            if reviews:
                st.markdown("**Reviews:**")
                for r in reviews:
                    author = r.get("author")
                    content = r.get("content", "").strip()
                    snippet = content[:300] + ("..." if len(content) > 300 else "")
                    st.markdown(f"- **{author}**: {snippet}")

        # -------------------------
        # Recommendations Section
        # -------------------------

        st.markdown("## Recommended Movies")

        recommendations = get_recommendations_by_id(movie_id)

        if recommendations:
            cols = st.columns(5)

            for i, rec in enumerate(recommendations):
                tmdb_rec = search_tmdb(rec["title"])
                if tmdb_rec:
                    rec_movie = tmdb_rec[0]
                    poster = get_poster_url(rec_movie.get("poster_path"))

                    with cols[i % 5]:
                        if poster:
                            st.image(poster)
                        # movie buttons to drill down on recs (title below poster)
                        if st.button(rec["title"], key=f"rec_{i}"):
                            # lookup TMDB immediately to get movie id and avoid transient 'not found'
                            tmdb_res = search_tmdb(rec["title"])
                            if tmdb_res:
                                st.session_state['selected_movie_id'] = tmdb_res[0].get("id")
                            st.session_state['selected_title'] = rec["title"]
                            st.session_state['clear_search'] = True
        else:
            st.info("No recommendations found.")
else:
    # no movie selected yet: show popular gallery
    st.markdown("## Popular Movies")
    popular = get_popular_movies()
    if popular:
        cols = st.columns(5)
        for i, movie in enumerate(popular[:20]):
            poster = get_poster_url(movie.get("poster_path"))
            with cols[i % 5]:
                if poster:
                    st.image(poster)
                if st.button(movie.get("title"), key=f"pop_{i}"):
                    # store id immediately so details show on first click
                    st.session_state['selected_movie_id'] = movie.get("id")
                    st.session_state['selected_title'] = movie.get("title")
                    st.session_state['clear_search'] = True
    else:
        st.write("Unable to load popular movies.")