import uvicorn
from fastapi import FastAPI, HTTPException
from recommender import HybridRecommender

# -------------------------------------------------
# Initialize recommender once (loads models once)
# -------------------------------------------------

recommender = HybridRecommender()

app = FastAPI(
    title="Hybrid Movie Recommender API",
    description="SBERT + TF-IDF hybrid item-item recommender",
    version="1.0"
)

# -------------------------------------------------
# Health Check
# -------------------------------------------------

@app.get("/")
def health():
    return {"status": "running"}

# -------------------------------------------------
# Recommend by Movie ID
# -------------------------------------------------

@app.get("/recommend/id/{movie_id}")
def recommend_by_id(movie_id: int, top_n: int = 10):
    try:
        results = recommender.recommend_by_id(movie_id, top_n)
        return {
            "query_type": "movie_id",
            "movie_id": movie_id,
            "recommendations": results
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Movie ID not found")

# -------------------------------------------------
# Recommend by Movie Title
# -------------------------------------------------

@app.get("/recommend/title/{movie_title}")
def recommend_by_title(movie_title: str, top_n: int = 10):
    try:
        results = recommender.recommend_by_title(movie_title, top_n)
        return {
            "query_type": "title",
            "movie_title": movie_title,
            "recommendations": results
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Movie title not found")

# -------------------------------------------------
# Optional: Search Titles
# Useful for autocomplete in web apps
# -------------------------------------------------

@app.get("/search")
def search_movies(query: str, limit: int = 10):
    query = query.lower()
    matches = [
        title for title in recommender.titles
        if query in str(title).lower()
    ]

    return {
        "query": query,
        "results": matches[:limit]
    }
#Run
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)