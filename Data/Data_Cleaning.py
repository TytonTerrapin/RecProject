import pandas as pd
import numpy as np
import ast
import re

INPUT_FILE = "Data/tmdb_movies_dataset.csv"
OUTPUT_FILE = "Data/tmdb_movies_cleaned.csv"

# -----------------------
# Helper Functions
# -----------------------

def safe_literal_eval(x):
    """Safely convert string list representation to Python list."""
    if pd.isna(x):
        return []
    if isinstance(x, list):
        return x
    try:
        return ast.literal_eval(x)
    except:
        return []

def clean_text(text):
    """Basic text cleaning."""
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)       # remove extra spaces
    return text.strip()

def clean_list_column(col):
    """Ensure list format, remove duplicates, lowercase."""
    cleaned = []
    for item in col:
        lst = safe_literal_eval(item)
        lst = list(set([str(x).lower().strip() for x in lst if str(x).strip() != ""]))
        cleaned.append(lst)
    return cleaned

df = pd.read_csv(INPUT_FILE)

print("Initial shape:", df.shape)

df = df.sort_values("popularity", ascending=False)
df = df.drop_duplicates(subset=["movie_id"], keep="first")

print("After removing duplicates:", df.shape)

df = df[df["overview"].notna()]
df = df[df["overview"].str.strip() != ""]
df = df[df["overview"].str.len() > 50]

print("After overview filtering:", df.shape)

df = df[df["vote_count"] >= 15]

print("After vote count filtering:", df.shape)

df["overview"] = df["overview"].apply(clean_text)

for col in ["genres", "cast", "keywords"]:
    if col in df.columns:
        df[col] = clean_list_column(df[col])

# Clean director column
if "director" in df.columns:
    df["director"] = df["director"].apply(lambda x: clean_text(str(x)))


df["popularity_log"] = np.log1p(df["popularity"])

df["popularity_norm"] = (
    df["popularity_log"] - df["popularity_log"].min()
) / (
    df["popularity_log"].max() - df["popularity_log"].min()
)

df["vote_average_norm"] = df["vote_average"] / 10.0

df["release_year"] = pd.to_datetime(
    df["release_date"], errors="coerce"
).dt.year


df = df[df["release_year"].notna()]
df = df[df["release_year"] >= 1950]

print("After release year filtering:", df.shape)

df.to_csv(OUTPUT_FILE, index=False)

print("Cleaned dataset saved as:", OUTPUT_FILE)
print("Final shape:", df.shape)