# 🎬 Movie Recommender System

A hybrid recommendation engine that suggests movies based on semantic and metadata similarity. Built with Streamlit frontend, FastAPI backend, and machine learning models trained on TMDB data.

## Features

- **Hybrid Recommendations** - Combines SBERT semantic embeddings + TF-IDF metadata analysis
- **Movie Search** - Search by title across 8,000+ cleaned movies
- **Popular Movies** - Browse trending and popular films
- **Rich Details** - View cast, genres, reviews, ratings, and more
- **TMDB Integration** - Live data syncing with The Movie Database API

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| ML Models | Scikit-learn, Sentence-Transformers |
| Data | Pandas, TMDB API |

## Quick Start (Local)

### Prerequisites
- Python 3.8+
- TMDB API Key (free from [themoviedb.org](https://www.themoviedb.org/settings/api))

### Setup

1. **Clone and activate environment**
   ```bash
   cd RecProject
   ./rec/Scripts/Activate.ps1  # Windows
   # or: source rec/bin/activate  # Linux/Mac
   ```

2. **Create `.env` file**
   ```
   TMDB_API_KEY=your_api_key_here
   API_BASE_URL=http://127.0.0.1:8000
   ```

3. **Start FastAPI backend** (Terminal 1)
   ```bash
   uvicorn api:app --reload
   ```

4. **Start Streamlit frontend** (Terminal 2)
   ```bash
   streamlit run app.py
   ```

5. **Open** `http://localhost:8501`

## Project Structure

```
RecProject/
├── app.py                    # Streamlit frontend
├── api.py                    # FastAPI backend
├── recommender.py            # ML recommendation engine
├── utils.py                  # Helper utilities
├── tmdb_api.py              # TMDB API integration
├── requirements.txt         # Python dependencies
│
├── Data/
│   ├── tmdb_movies_cleaned.csv    # 8,000+ movie dataset
│   └── Data_*.py               # Data processing scripts
│
└── models/
    ├── sbert_embeddings.npy   # Semantic embeddings
    ├── tfidf_matrix.npz       # TF-IDF matrix
    ├── movie_ids.npy          # Movie ID mappings
    └── titles.npy             # Movie titles
```

## How It Works

1. **Search/Browse** → Users find movies in cleaned dataset
2. **Select Movie** → API validates movie exists in dataset
3. **Generate Recommendations** → Hybrid model scores similarity:
   - Semantic: SBERT embeddings (overview/description)
   - Metadata: TF-IDF of genres, cast, director
4. **Combine Scores** → Weighted average (70% semantic, 30% metadata)
5. **Enrich Results** → Fetch posters, ratings from TMDB API

## Deployment

See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for cloud deployment guide.

**Quick summary:**
1. Deploy FastAPI backend (Render/Railway/Heroku)
2. Push code to GitHub
3. Connect to Streamlit Cloud
4. Add secrets: `TMDB_API_KEY` and `API_BASE_URL`
5. Deploy

## Key Files

- **app.py** - Main Streamlit app (main file for deployment)
- **api.py** - FastAPI server with `/api/movies/*` and `/api/recommendations/*` endpoints
- **recommender.py** - HybridRecommender class with SBERT/TF-IDF logic
- **utils.py** - Data loading, dataset filtering, enrichment functions
- **tmdb_api.py** - TMDB API wrapper with caching and retry logic

## Important Notes

✅ **Only dataset movies shown** - Movies are filtered to ensure recommendations work  
✅ **Cached embeddings** - Models pre-trained and saved (no retraining needed)  
✅ **Fast inferences** - Recommendations generated in milliseconds  

## Future Enhancements

- User rating-based collaborative filtering
- Movie watchlist/favorites
- Advanced filtering (year, rating, genre)
- Admin analytics dashboard

## License

Open source

## Contact

For issues or questions, refer to project documentation or TMDB API docs.
