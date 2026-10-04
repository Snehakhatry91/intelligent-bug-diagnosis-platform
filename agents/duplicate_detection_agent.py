"""
Duplicate Detection Agent
Identifies potential duplicates and related historical defects using vector similarity
and the single centralized threshold policy.
"""

from typing import List, Tuple
from agents.base_agent import BaseAgent
from backend.config import settings
from backend.models.schemas import DuplicateClassification, DuplicateDetectionResult, HistoricalEvidenceItem
from rag.retrieval_engine import retrieval_engine


class DuplicateDetectionAgent(BaseAgent):
    """Evaluates vector similarity against historical issues and applies strict threshold gating."""

    def __init__(self):
        super().__init__(
            name="Duplicate Detection Agent",
            description="Identifies identical or related historical defects using centralized cosine similarity thresholds"
        )

    async def process(self, evidence_items: List[HistoricalEvidenceItem]) -> DuplicateDetectionResult:
        """
        Evaluate retrieved historical evidence to determine duplicate status.
        Only items with similarity_score >= settings.DUPLICATE_THRESHOLD (0.82) are considered duplicates.
        """
        if not evidence_items:
            return DuplicateDetectionResult(
                is_duplicate=False,
                top_matches=[],
                duplicate_threshold=settings.DUPLICATE_THRESHOLD,
                related_threshold=settings.RELATED_THRESHOLD,
                summary="No historical matches found above evidence threshold (0.45)."
            )

        top_match = evidence_items[0]
        is_dup = top_match.similarity_score >= settings.DUPLICATE_THRESHOLD

        if is_dup:
            summary = (
                f"Likely duplicate detected! High similarity match with {top_match.issue_id} "
                f"({top_match.project}) at {top_match.similarity_score * 100:.1f}% similarity "
                f"(>= duplicate threshold {settings.DUPLICATE_THRESHOLD})."
            )
        elif top_match.similarity_score >= settings.RELATED_THRESHOLD:
            summary = (
                f"Related historical issue identified: {top_match.issue_id} ({top_match.project}) "
                f"at {top_match.similarity_score * 100:.1f}% similarity. Not classified as duplicate."
            )
        else:
            summary = (
                f"Weak historical correlation ({top_match.similarity_score * 100:.1f}% similarity). "
                f"Defect is considered novel."
            )

        return DuplicateDetectionResult(
            is_duplicate=is_dup,
            top_matches=evidence_items,
            duplicate_threshold=settings.DUPLICATE_THRESHOLD,
            related_threshold=settings.RELATED_THRESHOLD,
            summary=summary
        )


duplicate_detection_agent = DuplicateDetectionAgent()
