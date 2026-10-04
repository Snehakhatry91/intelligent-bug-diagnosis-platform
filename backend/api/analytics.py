"""
Defect Analytics API Endpoints
Serves mathematically reconciled defect pattern analytics and distribution counts.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import AnalyticsSummary
from backend.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Defect Analytics"])


@router.get("", response_model=AnalyticsSummary)
async def get_analytics_dashboard(
    db: AsyncSession = Depends(get_db)
):
    """Retrieve defect pattern analytics with strict population reconciliation."""
    summary = await analytics_service.get_analytics_summary(db)
    return summary
