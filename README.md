# Movie Recommender

This repository contains a hybrid movie recommender (SBERT + TF-IDF) with a FastAPI backend and a Streamlit frontend.

## Project structure

- `api.py` - FastAPI application serving recommendations and search endpoints.
- `recommender.py` - Hybrid recommender class used by `api.py`.
- `app.py` - Streamlit frontend that calls the recommender API and TMDB to display movie details and recommendations.
- `models/` - (not checked in) directory expected to contain `.npy` and `.npz` model artifacts (titles, embeddings, tfidf matrix, etc.).
- `Data/` - data collection utilities (e.g., `Data_Collection.py`).

## Requirements

Create and activate a Python virtual environment and install dependencies. Example (Windows PowerShell):

```powershell
python -m venv rec\
.\rec\Scripts\Activate.ps1
pip install -r requirements.txt
# If there is no requirements.txt, at minimum install:
# pip install streamlit requests python-dotenv fastapi uvicorn numpy scipy scikit-learn tqdm
```

## Environment variables

Create a `.env` file in the project root with the following:

```
TMDB_API_KEY=your_tmdb_api_key_here
# Optional: if the recommender backend runs on a different host
RECOMMENDER_API=http://127.0.0.1:8000
```

## Running the recommender API (backend)

Start the backend in one terminal (loads models; make sure `models/` exists and contains the required arrays):

```powershell
python api.py
# or (recommended during development):
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API exposes endpoints:
- `GET /` - health check
- `GET /recommend/id/{movie_id}` - recommendations by TMDB movie id
- `GET /recommend/title/{movie_title}` - recommendations by title
- `GET /search?query=...` - simple title search for autocomplete

## Running the Streamlit frontend

In another terminal, run:

```powershell
streamlit run app.py
```

The app will attempt to talk to the recommender API at `RECOMMENDER_API` (defaults to `http://127.0.0.1:8000`). If the backend isn't running the UI will still load but recommendations/autocomplete will be disabled.

### Deploying on Streamlit Community Cloud

To deploy the application to Streamlit's hosting (formerly Streamlit Sharing):

1. **Push your repository to GitHub.**
2. **Include a `requirements.txt`** (already provided in this repo).
3. **Set secrets/environment variables** via the Streamlit Cloud dashboard:
   - `TMDB_API_KEY`: your TMDB key.
   - `RECOMMENDER_API`: if you host the FastAPI backend separately, set its URL; otherwise leave blank and run backend as part of the same app using `multiprocessing` or similar.

4. **Optional:** if you need the backend logic to run on the same server, create a `Procfile` or modify `app.py` to start FastAPI in a thread; ensure model files are accessible.

5. Click "New app" in the Cloud, select your GitHub repo and the branch, and provide the path to `app.py` as the main file.

Because the recommender model files (`models/`) are not part of the repository, you'll need a way to either generate them on startup or store them in Git LFS / external storage.

> **Note:** Streamlit Cloud has limitations on long-running background processes; it's often simpler to host the FastAPI backend elsewhere (e.g., Heroku, Fly, Vercel) and point `RECOMMENDER_API` at it.

Deployment troubleshooting:

- Ensure `requirements.txt` lists all dependencies.
- Use the "Secrets" tab to configure TMDB_API_KEY.
- Check logs via the Cloud UI if the app fails to start.

## Notes

- The Streamlit UI uses a local cache for TMDB search results to reduce API calls.
- The backend expects precomputed model files in `models/` (e.g., `titles.npy`, `sbert_embeddings.npy`, `tfidf_matrix.npz`, `movie_ids.npy`).
- If you need help generating the model artifacts or packaging this for deployment, open an issue or ask for instructions.

## Troubleshooting

- If requests fail with connection errors, ensure the backend is running and your `TMDB_API_KEY` is valid.
- For object arrays (`.npy`) loading errors, the code uses `allow_pickle=True` where necessary; only load `.npy` files you trust.

---

Created to help run and test the hybrid movie recommender locally.
