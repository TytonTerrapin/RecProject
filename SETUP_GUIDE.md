# Movie Recommender System

A modern, full-stack movie recommendation application built with **FastAPI** backend and **Streamlit** frontend. The system uses a hybrid recommendation engine that combines semantic embeddings (SBERT) with metadata-based TF-IDF similarity.

## 📋 Features

### Core Features
- 🎬 **Hybrid Recommendation Engine**: Combines semantic and metadata-based recommendations
- 🔍 **Movie Search**: Full-text search across movie titles and metadata
- 🎯 **Popular Movies Gallery**: Browse top movies with beautiful posters
- 📊 **Movie Details**: View comprehensive movie information including cast, director, genres, and ratings
- 🎪 **Recommendations**: Get similar movie recommendations with relevance scores
- 🎨 **Responsive UI**: Beautiful, intuitive Streamlit interface with poster galleries

### Technical Stack
- **Backend**: FastAPI with CORS support
- **Frontend**: Streamlit with responsive gallery layout
- **ML Model**: Hybrid recommender (SBERT + TF-IDF)
- **Data**: TMDB dataset with 1000+ movies

## 🏗️ Project Structure

```
RecProject/
├── api.py                      # FastAPI backend application
├── app.py                      # Streamlit frontend application
├── recommender.py              # Core recommendation engine
├── utils.py                    # Utility functions for data loading
├── requirements.txt            # Python dependencies
├── Data/
│   ├── tmdb_movies_cleaned.csv # Cleaned movie dataset
│   ├── Data_Collection.py      # Original data collection script
│   └── Data_Cleaning.py        # Original data cleaning script
├── Encoder/
│   └── encoders.py             # Encoding pipeline
└── models/
    ├── sbert_embeddings.npy    # SBERT embeddings
    ├── tfidf_matrix.npz        # TF-IDF matrix
    ├── movie_ids.npy           # Movie ID mappings
    └── titles.npy              # Movie titles
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)

### Installation

1. **Clone/Navigate to the repository**
```bash
cd d:\RecProject
```

2. **Activate the virtual environment**
```bash
# On Windows
.\rec\Scripts\Activate.ps1

# On macOS/Linux
source rec/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

The application consists of two components that should run simultaneously:

#### Terminal 1: Start the FastAPI Backend
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

Output should show:
```
Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 2: Start the Streamlit Frontend
```bash
streamlit run app.py
```

Output should show:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## 📱 Usage

### 1. Browse Popular Movies
- Open the Streamlit app in your browser (http://localhost:8501)
- View the popular movies gallery below the search bar
- Each movie displays its poster, title, and rating

### 2. Search for Movies
- Use the search bar at the top to find specific movies
- Type a movie title and click "Search"
- Browse the search results

### 3. View Movie Details
- Click on any movie poster to see detailed information
- View cast, director, genres, and rating
- Read the full movie overview

### 4. Get Recommendations
- On the movie details page, scroll down to see "Similar Movies You Might Like"
- View up to 10 recommended movies with relevance scores
- Click on any recommendation to get more details

## 🔌 API Endpoints

The FastAPI backend provides the following endpoints:

### Health & Status
- `GET /` - Health check endpoint

### Movies
- `GET /api/movies/popular` - Get popular movies
  - Parameters: `limit` (1-100, default: 20)
  
- `GET /api/movies/search` - Search movies by title
  - Parameters: `q` (search query), `limit` (1-100, default: 50)
  
- `GET /api/movies/{movie_id}` - Get detailed movie information
  - Parameters: `movie_id` (TMDB movie ID)

### Recommendations
- `GET /api/recommendations/{movie_id}` - Get recommendations for a movie
  - Parameters: `movie_id`, `top_n` (1-50, default: 10)
  
- `POST /api/recommendations/by-title` - Get recommendations by movie title
  - Parameters: `title`, `top_n` (1-50, default: 10)

### API Documentation
- Interactive API docs: http://127.0.0.1:8000/docs
- Alternative docs: http://127.0.0.1:8000/redoc

## 📊 Recommendation Algorithm

The hybrid recommendation system uses:

1. **SBERT (Sentence-BERT)** Embeddings
   - Semantic similarity based on movie overviews
   - Captures plot and thematic similarities
   - Weight: 70% (Alpha)

2. **TF-IDF Metadata**
   - Matches genres, cast, director, keywords
   - Captures metadata similarities
   - Weight: 30% (Beta)

3. **Hybrid Ranking**
   - Combines top-50 semantic candidates with top-50 metadata candidates
   - Re-ranks union of candidates using weighted score
   - Returns top-N final recommendations

### Customization
To adjust recommendation weights, modify in `recommender.py`:
```python
recommender = HybridRecommender(
    alpha=0.7,  # SBERT weight
    beta=0.3,   # TF-IDF weight
    k_desc=50,  # Semantic candidates
    k_meta=50   # Metadata candidates
)
```

## ⚙️ Configuration

### Streamlit Configuration (`.streamlit/config.toml`)
Create optional file to customize Streamlit settings:
```toml
[theme]
primaryColor="#1f77b4"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f0f2f6"

[client]
maxUploadSize=200

[server]
maxConcurrentStreams=20
```

### API Configuration
Default settings in `api.py`:
- Host: `127.0.0.1`
- Port: `8000`
- CORS: Enabled for all origins

## 🐛 Troubleshooting

### "Could not connect to API" error
- Ensure FastAPI backend is running on http://127.0.0.1:8000
- Check that both terminals are active
- Verify no port conflicts (8000 and 8501)

### Movies not loading
- Check that `Data/tmdb_movies_cleaned.csv` exists
- Verify all model files in `models/` directory exist
- Check console output for loading errors

### Slow recommendations
- First run loads and caches models (may take a few seconds)
- Subsequent requests should be fast
- Clear Streamlit cache if issues persist: `streamlit cache clear`

### Import errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)
- Reinstall sentence-transformers if needed: `pip install --upgrade sentence-transformers`

## 📈 Performance Notes

- **Data Loading**: Models are cached in memory for fast access
- **First Request**: Initial SBERT model load (~50MB) takes a few seconds
- **Typical Recommendation Time**: <100ms per request
- **Supported Movies**: 1000+ from TMDB dataset

## 🔐 Security Considerations

- CORS is currently open to all origins (fine for local use)
- For production, restrict CORS to specific domains
- API has no authentication (add if deploying publicly)

## 📝 Development Notes

### Adding New Features

**Custom Search Filters**:
Modify `search_movies()` in `utils.py` to add filters by year, genre, rating, etc.

**New Endpoints**:
Add routes to `api.py` following FastAPI patterns with proper Pydantic models

**UI Improvements**:
Customize Streamlit layout in `app.py` using columns, tabs, and expanders

### Performance Optimization

- Consider caching recommendations
- Implement pagination for large result sets
- Add search query caching for common searches

## 📄 License

This project uses the TMDB dataset. Respect their terms of service.

## 👨‍💻 Author Notes

Built as a complete full-stack movie recommender with modern ML techniques and clean architecture. The separation of FastAPI backend and Streamlit frontend allows for easy scaling and integration with other applications.

For questions or improvements, feel free to modify the code!

---

**Last Updated**: March 2026
**API Version**: 1.0.0
**Python Version**: 3.9+
