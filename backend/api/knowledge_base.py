"""
Knowledge Base API Endpoints
Handles verified resolution listing and human-in-the-loop knowledge base promotion.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.db_models import KnowledgeBaseEntry
from backend.models.schemas import KBEntryResponse, KBVerificationRequest
from rag.kb_growth_manager import kb_growth_manager

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base Growth"])


@router.get("", response_model=List[KBEntryResponse])
async def list_verified_entries(
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all human-verified knowledge base entries."""
    q = select(KnowledgeBaseEntry).order_by(KnowledgeBaseEntry.verified_at.desc())
    res = await db.execute(q)
    return list(res.scalars().all())


@router.post("/promote", response_model=KBEntryResponse, status_code=status.HTTP_201_CREATED)
async def promote_verified_bug(
    payload: KBVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Promote a human-verified defect resolution into active RAG memory.
    Chunks, embeds, and updates the vector index.
    """
    try:
        entry = await kb_growth_manager.promote_verified_bug(db, payload)
        await db.commit()
        return entry
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Promotion failed: {str(e)}"
        )
