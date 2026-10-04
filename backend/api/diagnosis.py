"""
Bug Diagnosis & Orchestration API Endpoints
Triggers the multi-agent DAG pipeline, persists diagnosis records, and retrieves canonical context.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from agents.orchestrator import orchestrator
from backend.database import get_db
from backend.models.db_models import AnalysisResultRecord, BugSubmission
from backend.models.schemas import (
    BugAnalysisContext,
    ProcessingStatus,
    SubmissionResponse,
)

router = APIRouter(prefix="/diagnosis", tags=["Bug Diagnosis"])


@router.post("/run/{submission_id}", response_model=BugAnalysisContext)
async def run_bug_diagnosis(
    submission_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute end-to-end multi-agent diagnostic pipeline:
    Triage -> Log Analysis -> RAG Retrieval -> Duplicate Detection -> Root Cause -> Remediation
    """
    # 1. Fetch submission
    sub_query = select(BugSubmission).where(BugSubmission.id == submission_id)
    res = await db.execute(sub_query)
    submission = res.scalar_one_or_none()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bug submission '{submission_id}' not found."
        )

    submission.status = ProcessingStatus.PROCESSING.value
    await db.commit()

    # Convert to Pydantic schema for orchestrator
    sub_dto = SubmissionResponse.model_validate(submission)

    try:
        # 2. Run Orchestrator
        canonical_context = await orchestrator.execute_diagnosis(sub_dto)

        # 3. Persist Analysis Record
        top_dup = (
            canonical_context.duplicate_detection.top_matches[0]
            if canonical_context.duplicate_detection and canonical_context.duplicate_detection.top_matches
            else None
        )

        # Check if record already exists (re-run scenario)
        existing_q = select(AnalysisResultRecord).where(AnalysisResultRecord.submission_id == submission_id)
        existing_res = await db.execute(existing_q)
        analysis_record = existing_res.scalar_one_or_none()

        sev_val = canonical_context.triage.severity.value if canonical_context.triage else "Unknown"
        pri_val = canonical_context.triage.priority.value if canonical_context.triage else "Medium"
        comp_val = canonical_context.triage.affected_component if canonical_context.triage else "General"
        conf_val = canonical_context.triage.confidence if canonical_context.triage else 0.5
        hyp_val = canonical_context.root_cause.hypothesis if canonical_context.root_cause else "Diagnosis incomplete."
        rc_conf = canonical_context.root_cause.confidence if canonical_context.root_cause else 0.5
        is_dup = canonical_context.duplicate_detection.is_duplicate if canonical_context.duplicate_detection else False

        context_json = canonical_context.model_dump_json()

        if existing_record := analysis_record:
            existing_record.severity = sev_val
            existing_record.priority = pri_val
            existing_record.affected_component = comp_val
            existing_record.confidence = conf_val
            existing_record.exception_type = canonical_context.log_analysis.exception_type if canonical_context.log_analysis else None
            existing_record.error_message = canonical_context.log_analysis.error_message if canonical_context.log_analysis else None
            existing_record.failure_point = canonical_context.log_analysis.failure_point if canonical_context.log_analysis else None
            existing_record.affected_code_path = canonical_context.log_analysis.affected_code_path if canonical_context.log_analysis else None
            existing_record.root_cause_hypothesis = hyp_val
            existing_record.root_cause_confidence = rc_conf
            existing_record.is_duplicate = is_dup
            existing_record.top_duplicate_id = top_dup.issue_id if top_dup else None
            existing_record.top_duplicate_score = top_dup.similarity_score if top_dup else None
            existing_record.canonical_context_json = context_json
        else:
            new_record = AnalysisResultRecord(
                submission_id=submission_id,
                severity=sev_val,
                priority=pri_val,
                affected_component=comp_val,
                confidence=conf_val,
                exception_type=canonical_context.log_analysis.exception_type if canonical_context.log_analysis else None,
                error_message=canonical_context.log_analysis.error_message if canonical_context.log_analysis else None,
                failure_point=canonical_context.log_analysis.failure_point if canonical_context.log_analysis else None,
                affected_code_path=canonical_context.log_analysis.affected_code_path if canonical_context.log_analysis else None,
                root_cause_hypothesis=hyp_val,
                root_cause_confidence=rc_conf,
                is_duplicate=is_dup,
                top_duplicate_id=top_dup.issue_id if top_dup else None,
                top_duplicate_score=top_dup.similarity_score if top_dup else None,
                canonical_context_json=context_json
            )
            db.add(new_record)

        submission.status = ProcessingStatus.COMPLETED.value
        await db.commit()

        return canonical_context

    except Exception as e:
        submission.status = ProcessingStatus.FAILED.value
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnostic pipeline execution encountered fatal error: {str(e)}"
        )


@router.get("/{submission_id}", response_model=BugAnalysisContext)
async def get_diagnosis_result(
    submission_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full canonical BugAnalysisContext for a previously analyzed submission."""
    q = select(AnalysisResultRecord).where(AnalysisResultRecord.submission_id == submission_id)
    res = await db.execute(q)
    record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No diagnosis record exists for submission '{submission_id}'."
        )

    context_dict = json.loads(record.canonical_context_json)
    return BugAnalysisContext.model_validate(context_dict)
