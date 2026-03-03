import os
import numpy as np
import pandas as pd
import joblib
from tqdm import tqdm
from scipy import sparse
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# ----------------------------
# Configuration
# ----------------------------

INPUT_FILE = "Data/tmdb_movies_cleaned.csv"
OUTPUT_DIR = "models"
SBERT_MODEL_NAME = "all-MiniLM-L6-v2"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------
# Load Cleaned Dataset
# ----------------------------

df = pd.read_csv(INPUT_FILE)

print("Loaded dataset:", df.shape)

# ----------------------------
# 1️⃣ SBERT Embeddings (Overview)
# ----------------------------

print("Loading SBERT model...")
sbert_model = SentenceTransformer(SBERT_MODEL_NAME)

print("Generating SBERT embeddings...")
overview_texts = df["overview"].fillna("").tolist()

sbert_embeddings = sbert_model.encode(
    overview_texts,
    batch_size=64,
    show_progress_bar=True,
    convert_to_numpy=True
)

# Normalize embeddings for cosine similarity
sbert_embeddings = normalize(sbert_embeddings)

np.save(os.path.join(OUTPUT_DIR, "sbert_embeddings.npy"), sbert_embeddings)

print("SBERT embeddings saved.")

# ----------------------------
# 2️⃣ TF-IDF for Metadata
# ----------------------------

print("Preparing metadata text...")

def combine_metadata(row):
    genres = " ".join(eval(row["genres"])) if isinstance(row["genres"], str) else ""
    keywords = " ".join(eval(row["keywords"])) if isinstance(row["keywords"], str) else ""
    cast = " ".join(eval(row["cast"])) if isinstance(row["cast"], str) else ""
    director = row["director"] if isinstance(row["director"], str) else ""
    
    return f"{genres} {keywords} {director} {cast}"

meta_texts = df.apply(combine_metadata, axis=1)

print("Building TF-IDF vectorizer...")

tfidf_vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    stop_words="english"
)

tfidf_matrix = tfidf_vectorizer.fit_transform(meta_texts)

# L2 normalize (cosine similarity ready)
tfidf_matrix = normalize(tfidf_matrix)

# Save TF-IDF matrix and vectorizer
sparse.save_npz(os.path.join(OUTPUT_DIR, "tfidf_matrix.npz"), tfidf_matrix)
joblib.dump(tfidf_vectorizer, os.path.join(OUTPUT_DIR, "tfidf_vectorizer.pkl"))

print("TF-IDF model saved.")

# ----------------------------
# 3️⃣ Save Movie Identifiers
# ----------------------------

np.save(os.path.join(OUTPUT_DIR, "movie_ids.npy"), df["movie_id"].values)
np.save(os.path.join(OUTPUT_DIR, "titles.npy"), df["title"].values)

print("Movie IDs and titles saved.")

# ----------------------------
# Done
# ----------------------------

print("\nAll model artifacts saved in:", OUTPUT_DIR)