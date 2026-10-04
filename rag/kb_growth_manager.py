"""
Knowledge Base Growth Manager
Promotes human-verified defect resolutions into the active RAG vector index.
Guarantees that only verified bugs enter the knowledge base to prevent hallucination pollution.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.db_models import KnowledgeBaseEntry, BugSubmission, AnalysisResultRecord
from backend.models.schemas import KBVerificationRequest, KBEntryResponse
from rag.text_chunker import text_chunker
from rag.embedder import embedder
from rag.vector_store import vector_store


class KnowledgeBaseGrowthManager:
    """Manages verified resolution ingestion into persistent vector memory."""

    @staticmethod
    async def promote_verified_bug(
        db: AsyncSession,
        request: KBVerificationRequest
    ) -> KBEntryResponse:
        """
        Promote a completed analysis to the verified knowledge base:
        1. Validates source submission and analysis exist.
        2. Records human verification in knowledge_base_entries table.
        3. Normalizes and chunks the verified solution.
        4. Generates dense embeddings.
        5. Inserts into vector store and persists index.
        """
        # 1. Fetch analysis and submission
        analysis_query = select(AnalysisResultRecord).where(AnalysisResultRecord.id == request.analysis_id)
        res = await db.execute(analysis_query)
        analysis = res.scalar_one_or_none()

        if not analysis:
            # Check if analysis_id was passed as submission_id
            sub_query = select(AnalysisResultRecord).where(AnalysisResultRecord.submission_id == request.analysis_id)
            res_sub = await db.execute(sub_query)
            analysis = res_sub.scalar_one_or_none()

        if not analysis:
            raise ValueError(f"Analysis record with ID '{request.analysis_id}' not found.")

        sub_record_query = select(BugSubmission).where(BugSubmission.id == analysis.submission_id)
        sub_res = await db.execute(sub_record_query)
        submission = sub_res.scalar_one_or_none()

        title = submission.title if submission else f"Verified Resolution: {analysis.affected_component}"
        now = datetime.now(timezone.utc)
        entry_id = str(uuid.uuid4())

        # 2. Persist in database
        kb_entry = KnowledgeBaseEntry(
            id=entry_id,
            submission_id=analysis.submission_id,
            title=title,
            component=analysis.affected_component,
            severity=analysis.severity,
            root_cause=request.confirmed_root_cause,
            resolution=request.confirmed_resolution,
            verified_by=request.verified_by,
            verification_notes=request.verification_notes,
            verified_at=now,
            vector_indexed=True
        )
        db.add(kb_entry)
        await db.flush()
        await db.refresh(kb_entry)

        # 3. Create synthetic historical-style record for chunking
        record_dict = {
            "issue_id": f"KB-{entry_id[:8].upper()}",
            "project": "Internal KB (Verified)",
            "source": "Human Verified Diagnosis",
            "title": title,
            "description": f"Root Cause: {request.confirmed_root_cause}",
            "component": analysis.affected_component,
            "severity": analysis.severity,
            "resolution": "RESOLVED",
            "fix_patch_summary": request.confirmed_resolution,
            "source_url": f"/knowledge-base/{entry_id}"
        }

        # 4. Chunk & Embed
        chunks = text_chunker.chunk_defect_record(record_dict)
        for chunk in chunks:
            chunk_vec = embedder.embed_text(chunk["text"])
            vector_store.add_document_chunk(chunk, chunk_vec)

        # 5. Persist index
        vector_store.save()

        return KBEntryResponse(
            id=kb_entry.id,
            submission_id=kb_entry.submission_id,
            title=kb_entry.title,
            component=kb_entry.component,
            severity=kb_entry.severity,
            root_cause=kb_entry.root_cause,
            resolution=kb_entry.resolution,
            verified_by=kb_entry.verified_by,
            verification_notes=kb_entry.verification_notes,
            verified_at=kb_entry.verified_at,
            vector_indexed=True
        )


kb_growth_manager = KnowledgeBaseGrowthManager()
