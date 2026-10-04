"""
Unit Tests for Analytics Reconciliation & Population Accounting
Validates strict mathematical integrity:
sum(severity_counts) == total_submissions
sum(priority_counts) == total_submissions
"""

import pytest
from backend.database import AsyncSessionLocal, init_db
from backend.services.analytics_service import analytics_service


@pytest.mark.asyncio
async def test_analytics_population_reconciliation():
    await init_db()
    async with AsyncSessionLocal() as session:
        summary = await analytics_service.get_analytics_summary(session)

        # Check total submissions matches status sum
        status_sum = summary.completed_analyses + summary.pending_analyses + summary.failed_analyses
        assert status_sum == summary.total_submissions

        # Check severity distribution strictly equals total submissions
        sev_sum = sum(item.count for item in summary.severity_distribution)
        assert sev_sum == summary.total_submissions

        # Check priority distribution strictly equals total submissions
        pri_sum = sum(item.count for item in summary.priority_distribution)
        assert pri_sum == summary.total_submissions

        # Verify automated reconciliation flag
        assert summary.reconciliation_verified is True
