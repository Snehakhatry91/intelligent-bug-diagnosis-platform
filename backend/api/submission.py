"""
Bug Submission API Endpoints
Provides REST endpoints for submitting text bugs, stack traces, logs, and uploading files.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import SubmissionCreate, SubmissionResponse
from backend.services.submission_service import SubmissionService

router = APIRouter(prefix="/submissions", tags=["Bug Submission"])


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_bug_text(
    payload: SubmissionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit bug report, stack trace, or error log via JSON payload."""
    submission = await SubmissionService.create_submission(db, payload)
    return submission


@router.post("/upload", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def upload_bug_file(
    file: UploadFile = File(..., description="Uploaded defect file (.txt, .log, .md, .json up to 5MB)"),
    title: Optional[str] = Form(None, description="Optional custom title for the bug"),
    environment_details: Optional[str] = Form(None, description="Optional environment context"),
    db: AsyncSession = Depends(get_db)
):
    """Upload bug log or trace file with 5MB validation and zero-execution enforcement."""
    submission = await SubmissionService.handle_file_upload(
        db=db,
        file=file,
        title=title,
        environment_details=environment_details
    )
    return submission


@router.get("", response_model=List[SubmissionResponse])
async def list_submissions(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve submitted bugs ordered chronologically."""
    items, _ = await SubmissionService.list_submissions(db, limit, offset)
    return items


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve single submission by UUID."""
    submission = await SubmissionService.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission with ID '{submission_id}' not found."
        )
    return submission
