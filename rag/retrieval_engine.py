"""
RAG Retrieval Engine
Implements semantic similarity querying against the historical defect knowledge base
using the unified centralized similarity policy:
- >= 0.82: Likely Duplicate
- 0.65 - 0.81: Related Issue
- 0.45 - 0.64: Weak Match
- < 0.45: Filtered out / Insufficient evidence
"""

from typing import List, Optional, Tuple
from backend.config import settings
from backend.models.schemas import DuplicateClassification, HistoricalEvidenceItem
from rag.embedder import embedder
from rag.vector_store import vector_store


class RetrievalEngine:
    """Retrieval service implementing strict similarity thresholds and anti-hallucination policies."""

    def __init__(self, store=vector_store, embed_client=embedder):
        self.store = store
        self.embed_client = embed_client

    def classify_similarity(self, score: float) -> DuplicateClassification:
        """Classify similarity score using the single centralized policy."""
        if score >= settings.DUPLICATE_THRESHOLD:
            return DuplicateClassification.LIKELY_DUPLICATE
        elif score >= settings.RELATED_THRESHOLD:
            return DuplicateClassification.RELATED_ISSUE
        elif score >= settings.WEAK_THRESHOLD:
            return DuplicateClassification.WEAK_MATCH
        else:
            return DuplicateClassification.NO_MATCH

    def retrieve_evidence(
        self,
        query_text: str,
        top_k: int = 5
    ) -> Tuple[List[HistoricalEvidenceItem], str]:
        """
        Query vector store for relevant historical defect records.
        Returns:
            Tuple of (List[HistoricalEvidenceItem], status_message)
        """
        if not query_text or not query_text.strip():
            return [], "Empty query provided; no retrieval performed."

        query_vec = self.embed_client.embed_text(query_text)
        # Search vector store down to weak threshold (0.45)
        raw_matches = self.store.search(
            query_vector=query_vec,
            top_k=top_k * 2,  # retrieve extra to deduplicate chunks of same issue_id
            min_threshold=settings.EVIDENCE_THRESHOLD
        )

        if not raw_matches:
            return [], "Insufficient historical evidence found."

        seen_issue_ids = set()
        evidence_items: List[HistoricalEvidenceItem] = []

        for chunk_meta, score in raw_matches:
            issue_id = chunk_meta.get("issue_id", "UNKNOWN")
            if issue_id in seen_issue_ids:
                continue
            seen_issue_ids.add(issue_id)

            classification = self.classify_similarity(score)

            evidence_items.append(
                HistoricalEvidenceItem(
                    issue_id=issue_id,
                    project=chunk_meta.get("project", "Unknown Project"),
                    title=chunk_meta.get("title", "Untitled Defect"),
                    similarity_score=round(score, 4),
                    classification=classification,
                    resolution=chunk_meta.get("resolution"),
                    fix_patch_summary=chunk_meta.get("fix_patch_summary"),
                    source_url=chunk_meta.get("source_url"),
                    component=chunk_meta.get("component")
                )
            )

            if len(evidence_items) >= top_k:
                break

        if not evidence_items:
            return [], "Insufficient historical evidence found."

        return evidence_items, f"Retrieved {len(evidence_items)} historical reference(s) meeting evidence threshold (>= {settings.EVIDENCE_THRESHOLD})."


retrieval_engine = RetrievalEngine()
