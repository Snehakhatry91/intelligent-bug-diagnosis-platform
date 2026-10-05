"""
Historical Defect Knowledge Base API Endpoints
Provides search, filtering, and retrieval of curated Mozilla, Apache, and Eclipse defects.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from backend.database import get_db
from backend.models.db_models import HistoricalDefect
from backend.models.schemas import HistoricalDefectSchema, HistoricalEvidenceItem
from rag.retrieval_engine import retrieval_engine

router = APIRouter(prefix="/historical", tags=["Historical Defect Knowledge Base"])


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.get("", response_model=List[HistoricalDefectSchema])
async def list_historical_defects(
    project: Optional[str] = Query(None, description="Filter by ecosystem (Mozilla, Apache, Eclipse)"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    search: Optional[str] = Query(None, description="Text filter in title or component"),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve indexed historical defect records with optional filtering."""
    query = select(HistoricalDefect)

    if project:
        query = query.where(HistoricalDefect.project.ilike(f"%{project}%"))
    if severity:
        query = query.where(HistoricalDefect.severity.ilike(severity))
    if search:
        search_fmt = f"%{search}%"
        query = query.where(
            or_(
                HistoricalDefect.title.ilike(search_fmt),
                HistoricalDefect.component.ilike(search_fmt),
                HistoricalDefect.issue_id.ilike(search_fmt)
            )
        )

    query = query.offset(offset).limit(limit)
    res = await db.execute(query)
    return list(res.scalars().all())


@router.get("/{issue_id}", response_model=HistoricalDefectSchema)
async def get_historical_defect(
    issue_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve single historical defect by upstream issue ID."""
    q = select(HistoricalDefect).where(HistoricalDefect.issue_id == issue_id)
    res = await db.execute(q)
    defect = res.scalar_one_or_none()

    if not defect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historical defect '{issue_id}' not found."
        )
    return defect


@router.post("/search", response_model=List[HistoricalEvidenceItem])
async def semantic_search_historical(
    payload: SemanticSearchRequest
):
    """Execute real semantic vector similarity search against historical corpus."""
    evidence, _ = retrieval_engine.retrieve_evidence(payload.query, top_k=payload.top_k)
    return evidence
