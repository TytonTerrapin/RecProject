# 🚀 Quick Start Guide

## One-Command Startup (Windows)

### Option 1: Using Batch Script
```bash
.\start.bat
```
This will automatically:
- Activate the virtual environment
- Start FastAPI backend (new window)
- Start Streamlit frontend (new window)

### Option 2: Using PowerShell Script
```powershell
.\start.ps1
```

## Manual Startup (If You Prefer)

### Terminal 1 - Start the API Backend
```bash
# Activate environment (if not already active)
.\rec\Scripts\Activate.ps1

# Start FastAPI
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

Wait for this output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 - Start the Frontend
```bash
# Activate environment (if not already active)
.\rec\Scripts\Activate.ps1

# Start Streamlit
streamlit run app.py
```

Wait for this output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## 📱 Access Your Application

Once both services are running, open in your web browser:

### Frontend (Browse & Recommend)
👉 **http://localhost:8501**

### API Documentation
👉 **http://127.0.0.1:8000/docs**
(Interactive API documentation with live testing)

## ⏹️ Stopping the Application

- **Keep windows open** while using the app for real-time interaction
- **Close windows** individually to stop each service
- Or press `Ctrl+C` in each terminal

## 🧪 Testing the API

Once the API is running, test it directly:

### Get Popular Movies
```bash
curl http://127.0.0.1:8000/api/movies/popular?limit=5
```

### Search for a Movie
```bash
curl "http://127.0.0.1:8000/api/movies/search?q=avatar"
```

### Get Movie Details (using movie_id from above)
```bash
curl http://127.0.0.1:8000/api/movies/19995  # Avatar movie ID
```

### Get Recommendations
```bash
curl "http://127.0.0.1:8000/api/recommendations/19995?top_n=10"
```

## 🔍 How to Use the Frontend

1. **Browse Popular Movies**: See top 20 movies in a gallery format on home page
2. **Search**: Use the search bar to find movies by title
3. **View Details**: Click on any movie poster to see full details
4. **Get Recommendations**: Scroll down to see similar movies recommended by the AI
5. **Explore**: Click on any recommended movie to get its details and recommendations

## 📊 Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Streamlit Frontend                              │
│    (User Interface - Web Gallery & Search)              │
└─────────────┬───────────────────────────────────────────┘
              │
              │ HTTP/REST Requests
              │
┌─────────────▼───────────────────────────────────────────┐
│         FastAPI Backend                                 │
│    (API Endpoints - Search, Details, Recommendations)   │
└─────────────┬───────────────────────────────────────────┘
              │
              │ In-Memory Access
              │
┌─────────────▼───────────────────────────────────────────┐
│      Recommendation Engine                              │
│   (HybridRecommender - SBERT + TF-IDF)                  │
└─────────────┬───────────────────────────────────────────┘
              │
              │ Loads
              │
┌─────────────▼───────────────────────────────────────────┐
│      Pre-trained Models & Data                          │
│   (SBERT Embeddings, TF-IDF, Movie Database)            │
└─────────────────────────────────────────────────────────┘
```

## 💡 Tips

- **First Load**: The SBERT model (~50MB) loads on first API request - this takes ~5-10 seconds
- **Fast After**: Subsequent requests are very fast (<100ms)
- **Caching**: Results are cached, so the same searches load instantly
- **TMDB Posters**: Movie posters are loaded from TMDB's CDN in real-time

## ❌ Troubleshooting

**Frontend says "Could not connect to API"**
- Make sure FastAPI is running on Terminal 1
- Check that port 8000 is not blocked
- Restart both services

**Movies not loading**
- Ensure `Data/tmdb_movies_cleaned.csv` exists
- Check that all files in `models/` directory are present
- Verify trained models are in place

**Slow responses**
- This is normal on first request (model loading)
- Check API logs in Terminal 1 for any errors
- Try refreshing the browser after a few seconds

**Port already in use**
- If port 8000/8501 is busy, edit the startup scripts or use different ports
- To use custom ports: `streamlit run app.py --server.port 8502`

## 📚 Full Documentation

For more details, see **SETUP_GUIDE.md**

---

**Enjoy discovering movies! 🎬**
