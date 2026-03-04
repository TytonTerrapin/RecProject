import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


class HybridRecommender:
    def __init__(
        self,
        model_dir="models",
        alpha=0.6,
        beta=0.4,
        k_desc=50,
        k_meta=50
    ):

        print("Loading models...")

        self.sbert_embeddings = np.load(f"{model_dir}/sbert_embeddings.npy", allow_pickle=True)
        self.tfidf_matrix = sparse.load_npz(f"{model_dir}/tfidf_matrix.npz")

        self.movie_ids = np.load(f"{model_dir}/movie_ids.npy", allow_pickle=True)
        self.titles = np.load(f"{model_dir}/titles.npy", allow_pickle=True)

        # NEW: load genres
        self.genres = np.load(f"{model_dir}/genres.npy", allow_pickle=True)

        self.id_to_index = {
            self.movie_ids[i]: i for i in range(len(self.movie_ids))
        }

        self.title_to_index = {
            str(self.titles[i]).lower(): i
            for i in range(len(self.titles))
        }

        self.alpha = alpha
        self.beta = beta
        self.k_desc = k_desc
        self.k_meta = k_meta

        print("Models loaded.")

    # ---------------------------------------------------------
    # Core Recommendation Logic
    # ---------------------------------------------------------

    def _recommend_by_index(self, idx, top_n=10):

        # Compute similarities
        desc_sim = cosine_similarity(
            self.sbert_embeddings[idx].reshape(1, -1),
            self.sbert_embeddings
        ).flatten()

        meta_sim = cosine_similarity(
            self.tfidf_matrix[idx],
            self.tfidf_matrix
        ).flatten()

        # Remove self similarity
        desc_sim[idx] = -1
        meta_sim[idx] = -1

        # Top candidates from each similarity
        top_desc_idx = np.argpartition(desc_sim, -self.k_desc)[-self.k_desc:]
        top_meta_idx = np.argpartition(meta_sim, -self.k_meta)[-self.k_meta:]

        # Candidate union
        candidates = np.unique(
            np.concatenate([top_desc_idx, top_meta_idx])
        )
        
        meta_threshold = 0.05

        filtered = [
            c for c in candidates
            if meta_sim[c] > meta_threshold
                   ]

        if len(filtered) > top_n:
            candidates = np.array(filtered)
        # ---------------------------------------------------------
        # GENRE FILTER
        # ---------------------------------------------------------

        query_genres = set(self.genres[idx])

        filtered_candidates = [
            c for c in candidates
            if len(query_genres.intersection(self.genres[c])) > 0
        ]

        if len(filtered_candidates) > 0:
            candidates = np.array(filtered_candidates)

        # ---------------------------------------------------------
        # Normalize similarity scores
        # ---------------------------------------------------------

        desc_norm = (desc_sim - desc_sim.min()) / (
            desc_sim.max() - desc_sim.min() + 1e-8
        )

        meta_norm = (meta_sim - meta_sim.min()) / (
            meta_sim.max() - meta_sim.min() + 1e-8
        )

        # Hybrid scoring
        scores = (
            self.alpha * desc_norm[candidates] +
            self.beta * meta_norm[candidates]
        )

        # Rank candidates
        top_indices = np.argsort(scores)[-top_n:][::-1]
        final_candidates = candidates[top_indices]

        return [
            {
                "movie_id": int(self.movie_ids[i]),
                "title": self.titles[i],
                "score": float(scores[top_indices[j]])
            }
            for j, i in enumerate(final_candidates)
        ]

    # ---------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------

    def recommend_by_id(self, movie_id, top_n=10):

        if movie_id not in self.id_to_index:
            raise ValueError("Movie ID not found")

        idx = self.id_to_index[movie_id]
        return self._recommend_by_index(idx, top_n)

    def recommend_by_title(self, movie_title, top_n=10):

        movie_title = movie_title.lower()

        if movie_title not in self.title_to_index:
            raise ValueError("Movie title not found")

        idx = self.title_to_index[movie_title]
        return self._recommend_by_index(idx, top_n)