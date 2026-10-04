"""
Semantic Vector Embedder
Generates 384-dimensional dense semantic vector representations for defect texts and logs using
the local open-source SentenceTransformer ('sentence-transformers/all-MiniLM-L6-v2') model.
Runs completely locally with zero external API dependencies and zero API keys.
Vectors are unit-normalized so dot product equals cosine similarity.
"""

import os
from typing import List, Optional
import numpy as np

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
EMBEDDING_METRIC = "cosine"

INDEX_METADATA = {
    "embedding_model": EMBEDDING_MODEL_NAME,
    "embedding_dimension": EMBEDDING_DIMENSION,
    "metric": EMBEDDING_METRIC,
}


class SemanticEmbedder:
    """
    384-dimensional dense semantic embedder using sentence-transformers/all-MiniLM-L6-v2.
    Pretrained transformer produces unit-normalized semantic embeddings for bug reports,
    stack traces, error logs, and historical defect resolutions.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME, dimension: int = EMBEDDING_DIMENSION):
        self.model_name = model_name
        self.dimension = dimension
        self._model = None

    def _get_model(self):
        """Lazy-load the SentenceTransformer model on first usage."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            # Disable unnecessary symlink warnings on Windows
            os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate a 384-dimensional dense vector for a single text input.
        Returns a float32 numpy array with unit L2 norm.
        """
        if not text or not text.strip():
            vec = np.zeros(self.dimension, dtype=np.float32)
            vec[0] = 1.0
            return vec

        model = self._get_model()
        vec = model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype(np.float32)

        return vec

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Batch embedding of multiple texts. Returns (N, 384) float32 matrix with unit L2 norms.
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        sanitized_texts = [t if (t and t.strip()) else "empty" for t in texts]
        model = self._get_model()
        vectors = model.encode(
            sanitized_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        ).astype(np.float32)

        return vectors

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between two unit vectors."""
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        if v1_norm < 1e-9 or v2_norm < 1e-9:
            return 0.0
        u1 = v1 / v1_norm
        u2 = v2 / v2_norm
        dot = float(np.dot(u1, u2))
        return float(max(-1.0, min(1.0, dot)))


# Global singleton instance
embedder = SemanticEmbedder()
