# Streamlit Cloud Deployment Guide

## Prerequisites
1. GitHub account with your project repository
2. Streamlit Cloud account (free at https://share.streamlit.io)
3. FastAPI backend deployed on a server (required)

## Step 1: Deploy FastAPI Backend

Before deploying the Streamlit frontend, you must deploy the FastAPI backend. Here are popular options:

### Option A: Deploy to Render (Recommended - Free tier available)
1. Go to https://render.com
2. Create new Web Service from GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn api:app --host 0.0.0.0 --port 8000`
5. Copy the deployed URL (e.g., `https://your-api-app.onrender.com`)

### Option B: Deploy to Railway
1. Go to https://railway.app
2. Connect GitHub and select your repository
3. Set start command: `uvicorn api:app --host 0.0.0.0`
4. Copy the deployed URL

### Option C: Deploy to Heroku (Legacy)
1. Create `Procfile` in root:
   ```
   web: uvicorn api:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy via Heroku CLI

## Step 2: Configure Secrets on Streamlit Cloud

After deploying the backend, set up secrets:

1. Go to https://share.streamlit.io/
2. Click on your Streamlit app
3. Click "Settings" → "Secrets"
4. Add these secrets:

```toml
# Your TMDB API Key (get free key from https://www.themoviedb.org/settings/api)
TMDB_API_KEY = "your_actual_tmdb_api_key_here"

# Your deployed FastAPI backend URL (from Step 1)
API_BASE_URL = "https://your-deployed-api.onrender.com"
```

## Step 3: Deploy Streamlit App

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select GitHub repository
4. Set these options:
   - **Repository**: Your GitHub repo
   - **Branch**: main
   - **Main file path**: `app.py`
5. Click "Deploy"

Streamlit will automatically install dependencies from `requirements.txt` and start your app.

## Step 4: Verify Deployment

After deployment:
1. The Streamlit app should load
2. Try searching for a movie
3. Click "View Details" on a movie
4. Verify recommendations show correctly

## Troubleshooting

### "Could not connect to API" error
- Check that FastAPI backend is running and accessible
- Verify `API_BASE_URL` in secrets is correct
- Check backend CORS settings in `api.py`

### "TMDB_API_KEY not found"
- Verify secret is added in Streamlit Cloud dashboard
- Check spelling of secret key name
- Restart the app after adding secrets

### Movies not loading
- Ensure `Data/tmdb_movies_cleaned.csv` is committed to GitHub
- Check model files in `models/` directory exist
- Verify TMDB API key is valid

## Local Development Setup

To test locally before deployment:

1. Create `.env` file:
```
TMDB_API_KEY=your_tmdb_api_key_here
API_BASE_URL=http://127.0.0.1:8000
```

2. Run FastAPI backend:
```bash
uvicorn api:app --reload
```

3. Run Streamlit frontend (in another terminal):
```bash
streamlit run app.py
```

## Production Considerations

- Ensure TMDB API key has appropriate rate limits
- Monitor FastAPI backend performance
- Consider caching recommendations if traffic is high
- Keep data files in GitHub or use external storage service
- Monitor TMDB API costs

## Support

For Streamlit Cloud issues: https://discuss.streamlit.io/
For FastAPI deployment questions: Check your hosting provider's documentation
