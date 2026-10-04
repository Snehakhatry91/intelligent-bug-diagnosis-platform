"""
Unit Tests for RAG Pipeline Components
Tests text chunker, dense semantic embedder, vector store, and retrieval engine similarity thresholds.
"""

import numpy as np
import pytest
from backend.config import settings
from backend.models.schemas import DuplicateClassification
from rag.embedder import embedder
from rag.retrieval_engine import retrieval_engine
from rag.text_chunker import text_chunker
from rag.vector_store import vector_store


def test_chunk_defect_record_preserves_canonical_metadata():
    record = {
        "issue_id": "TEST-100",
        "project": "Apache",
        "component": "Core",
        "title": "Deadlock during transaction commit",
        "description": "A long description detailing how two threads entered AB-BA deadlock condition during commit.",
        "severity": "Critical",
        "resolution": "FIXED",
        "fix_patch_summary": "Replaced mutex lock with tryLock",
        "source_url": "https://issues.apache.org/test"
    }
    chunks = text_chunker.chunk_defect_record(record)
    assert len(chunks) >= 1
    primary = chunks[0]
    assert primary["issue_id"] == "TEST-100"
    assert primary["project"] == "Apache"
    assert "Deadlock during transaction commit" in primary["text"]


def test_embedder_generates_384_dim_unit_vectors():
    vec = embedder.embed_text("NullPointerException in payment method")
    assert vec.shape == (384,)
    norm = np.linalg.norm(vec)
    assert pytest.approx(norm, rel=1e-3) == 1.0


def test_cosine_similarity_calculation():
    v1 = embedder.embed_text("Database connection timeout deadlock")
    v2 = embedder.embed_text("Database connection timeout deadlock")
    sim = embedder.cosine_similarity(v1, v2)
    assert pytest.approx(sim, abs=1e-4) == 1.0


def test_retrieval_engine_similarity_policy_classification():
    # Exactly matches the single centralized policy in backend/config.py
    assert retrieval_engine.classify_similarity(0.85) == DuplicateClassification.LIKELY_DUPLICATE
    assert retrieval_engine.classify_similarity(0.82) == DuplicateClassification.LIKELY_DUPLICATE
    assert retrieval_engine.classify_similarity(0.70) == DuplicateClassification.RELATED_ISSUE
    assert retrieval_engine.classify_similarity(0.65) == DuplicateClassification.RELATED_ISSUE
    assert retrieval_engine.classify_similarity(0.50) == DuplicateClassification.WEAK_MATCH
    assert retrieval_engine.classify_similarity(0.45) == DuplicateClassification.WEAK_MATCH
    assert retrieval_engine.classify_similarity(0.40) == DuplicateClassification.NO_MATCH


def test_retrieval_returns_insufficient_evidence_for_novel_query():
    # Test query completely orthogonal to any software bug
    novel_query = "Recipe for chocolate chip cookies with organic vanilla bean extract"
    matches, status_msg = retrieval_engine.retrieve_evidence(novel_query)
    # Below 0.45, items must be filtered out
    assert matches == []
    assert "Insufficient historical evidence found" in status_msg
