"""
Vector Store and Index Manager
Maintains in-memory vector index with metadata, disk persistence, and exact cosine similarity search.
Integrates with the unified threshold policy.
"""

import os
import pickle
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from backend.config import settings
from rag.embedder import embedder


class VectorStore:
    """Persistent vector store for defect chunks and verified knowledge base items."""

    def __init__(self, index_path: Optional[str] = None):
        self.index_path = index_path or settings.VECTOR_INDEX_PATH
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None  # Shape (N, 384)
        self.load()

    def add_document_chunk(self, chunk_data: Dict[str, Any], vector: np.ndarray) -> None:
        """Add a single chunk and its embedding to the in-memory index."""
        self.chunks.append(chunk_data)
        vector_reshaped = vector.reshape(1, -1)
        if self.embeddings is None or len(self.embeddings) == 0:
            self.embeddings = vector_reshaped
        else:
            self.embeddings = np.vstack([self.embeddings, vector_reshaped])

    def add_batch(self, chunks: List[Dict[str, Any]], vectors: np.ndarray) -> None:
        """Batch insert chunks and embeddings."""
        self.chunks.extend(chunks)
        if self.embeddings is None or len(self.embeddings) == 0:
            self.embeddings = vectors
        else:
            self.embeddings = np.vstack([self.embeddings, vectors])

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        min_threshold: float = 0.0
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Perform exact cosine similarity search against indexed vectors.
        Returns sorted list of (chunk_metadata, cosine_similarity_score).
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        # Cosine similarity is dot product because vectors are unit normalized
        query_norm = np.linalg.norm(query_vector)
        if query_norm > 0:
            q_unit = query_vector / query_norm
        else:
            q_unit = query_vector

        scores = np.dot(self.embeddings, q_unit)

        # Pair scores with chunk metadata and sort
        scored_results: List[Tuple[Dict[str, Any], float]] = []
        for idx, score in enumerate(scores):
            score_val = float(score)
            if score_val >= min_threshold:
                scored_results.append((self.chunks[idx], score_val))

        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

    def save(self) -> None:
        """Persist vector index and metadata to disk."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings
        }
        with open(self.index_path, "wb") as f:
            pickle.dump(data, f)

    def load(self) -> bool:
        """Load vector index from disk if it exists."""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = data.get("chunks", [])
                    self.embeddings = data.get("embeddings", None)
                return True
            except Exception as e:
                print(f"[VectorStore] Warning: Could not load index at {self.index_path}: {e}")
                self.chunks = []
                self.embeddings = None
        return False

    def count(self) -> int:
        """Return total number of indexed chunks."""
        return len(self.chunks)

    def clear(self) -> None:
        """Clear all in-memory chunks and embeddings."""
        self.chunks = []
        self.embeddings = None


vector_store = VectorStore()
