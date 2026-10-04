"""
Vector Store and Index Manager
Maintains in-memory vector index with metadata, disk persistence, and exact cosine similarity search.
Integrates with the unified threshold policy and SentenceTransformer all-MiniLM-L6-v2 embeddings.
"""

import os
import pickle
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from backend.config import settings
from rag.embedder import EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION, EMBEDDING_METRIC, INDEX_METADATA


class VectorStore:
    """Persistent vector store for defect chunks and verified knowledge base items."""

    def __init__(self, index_path: Optional[str] = None):
        self.index_path = index_path or settings.VECTOR_INDEX_PATH
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None  # Shape (N, 384)
        self.metadata: Dict[str, Any] = dict(INDEX_METADATA)
        self.load()

    def exists(self) -> bool:
        """Check whether the vector index file exists on disk."""
        return os.path.exists(self.index_path)

    def is_ready(self) -> bool:
        """Return True if index exists on disk and has loaded embeddings."""
        return self.exists() and self.count() > 0 and self.embeddings is not None

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
        if query_norm > 1e-9:
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
            "metadata": {
                "embedding_model": EMBEDDING_MODEL_NAME,
                "embedding_dimension": EMBEDDING_DIMENSION,
                "metric": EMBEDDING_METRIC,
                "chunk_count": len(self.chunks),
            },
            "chunks": self.chunks,
            "embeddings": self.embeddings,
        }
        with open(self.index_path, "wb") as f:
            pickle.dump(data, f)
        self.metadata = data["metadata"]

    def load(self) -> bool:
        """Load vector index from disk if it exists and matches current embedding model."""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    metadata = data.get("metadata", {})
                    # Ensure compatibility: if index was created with older hashed model, ignore it
                    if metadata.get("embedding_model") != EMBEDDING_MODEL_NAME:
                        print(f"[VectorStore] Notice: Vector index was built with a different model ({metadata.get('embedding_model')}). Ingestion required.")
                        self.chunks = []
                        self.embeddings = None
                        return False
                    self.chunks = data.get("chunks", [])
                    self.embeddings = data.get("embeddings", None)
                    self.metadata = metadata
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
        self.metadata = dict(INDEX_METADATA)


vector_store = VectorStore()
