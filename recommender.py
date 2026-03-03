import numpy as np
import joblib
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


class HybridRecommender:
    def __init__(
        self,
        model_dir="models",
        alpha=0.7,
        beta=0.3,
        k_desc=50,
        k_meta=50
    ):
        """
        alpha: weight for SBERT similarity
        beta: weight for TF-IDF similarity
        k_desc: number of semantic candidates
        k_meta: number of metadata candidates
        """

        print("Loading models...")

        # load numpy arrays; some may contain object dtypes so allow_pickle
        self.sbert_embeddings = np.load(f"{model_dir}/sbert_embeddings.npy", allow_pickle=True)
        self.tfidf_matrix = sparse.load_npz(f"{model_dir}/tfidf_matrix.npz")
        self.movie_ids = np.load(f"{model_dir}/movie_ids.npy", allow_pickle=True)
        self.titles = np.load(f"{model_dir}/titles.npy", allow_pickle=True)

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

        # 1️⃣ Compute similarities
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

        # 2️⃣ Get Top-K from each
        top_desc_idx = np.argsort(desc_sim)[-self.k_desc:]
        top_meta_idx = np.argsort(meta_sim)[-self.k_meta:]

        # 3️⃣ Union of candidates
        candidates = set(top_desc_idx).union(set(top_meta_idx))

        # 4️⃣ Re-rank union
        results = []
        for i in candidates:
            score = self.alpha * desc_sim[i] + self.beta * meta_sim[i]
            results.append((i, score))

        results = sorted(results, key=lambda x: x[1], reverse=True)

        # 5️⃣ Return Top-N
        final = results[:top_n]

        return [
            {
                "movie_id": int(self.movie_ids[i]),
                "title": self.titles[i],
                "score": float(score)
            }
            for i, score in final
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