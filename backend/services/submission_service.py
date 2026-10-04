"""
Bug Submission Service
Handles text and file submissions with strict input sanitization, size validation,
null-byte stripping, and zero-execution guarantees.
"""

from datetime import datetime, timezone
import os
import re
import uuid
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.models.db_models import BugSubmission
from backend.models.schemas import InputType, ProcessingStatus, SubmissionCreate, SubmissionResponse


class SubmissionService:
    """Service handling bug ingestion with enterprise security and sanitization."""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitizes text by stripping null bytes and non-printable control characters,
        preserving standard newlines, tabs, and carriage returns.
        """
        if not text:
            return ""
        # Strip null bytes completely
        cleaned = text.replace("\x00", "")
        # Remove destructive control chars but preserve \n, \r, \t
        cleaned = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)
        return cleaned.strip()

    @classmethod
    async def create_submission(
        cls,
        db: AsyncSession,
        payload: SubmissionCreate
    ) -> BugSubmission:
        """Create and persist a submission from direct text input."""
        cleaned_title = cls.sanitize_text(payload.title)
        cleaned_content = cls.sanitize_text(payload.raw_content)

        if not cleaned_title or len(cleaned_title) < 3:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Title must be at least 3 characters of valid text."
            )
        if not cleaned_content or len(cleaned_content) < 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Content must be at least 5 characters of valid text."
            )

        # Detect input type if defaulted to bug_report
        input_type = payload.input_type.value
        if input_type == InputType.BUG_REPORT.value:
            if "Traceback (most recent call last)" in cleaned_content or "Exception in thread" in cleaned_content:
                input_type = InputType.STACK_TRACE.value
            elif re.search(r"\[\d{4}-\d{2}-\d{2}", cleaned_content) or "ERROR" in cleaned_content or "WARN" in cleaned_content:
                input_type = InputType.ERROR_LOG.value

        submission_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        submission = BugSubmission(
            id=submission_id,
            title=cleaned_title,
            raw_content=cleaned_content,
            input_type=input_type,
            environment_details=cls.sanitize_text(payload.environment_details) if payload.environment_details else None,
            file_name=payload.file_name,
            file_size_bytes=len(cleaned_content.encode("utf-8")),
            status=ProcessingStatus.PENDING.value,
            created_at=now,
            updated_at=now
        )

        db.add(submission)
        await db.flush()
        await db.refresh(submission)
        return submission

    @classmethod
    async def handle_file_upload(
        cls,
        db: AsyncSession,
        file: UploadFile,
        title: Optional[str] = None,
        environment_details: Optional[str] = None
    ) -> BugSubmission:
        """Validate, sanitize, and ingest uploaded files with zero-execution enforcement."""
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file has no filename.")

        # Validate file extension
        _, ext = os.path.splitext(file.filename.lower())
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File extension '{ext}' is not permitted. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Read content and enforce size ceiling (5 MB)
        content_bytes = await file.read()
        if len(content_bytes) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES / (1024*1024):.1f} MB."
            )

        if len(content_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file is empty."
            )

        try:
            raw_text = content_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to decode text file as valid UTF-8: {str(e)}"
            )

        sanitized_text = cls.sanitize_text(raw_text)
        if len(sanitized_text) < 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file contains no readable text after sanitization."
            )

        effective_title = title.strip() if title and title.strip() else f"Uploaded Defect File: {file.filename}"
        effective_title = cls.sanitize_text(effective_title)

        submission_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        submission = BugSubmission(
            id=submission_id,
            title=effective_title,
            raw_content=sanitized_text,
            input_type=InputType.FILE_UPLOAD.value,
            environment_details=cls.sanitize_text(environment_details) if environment_details else None,
            file_name=os.path.basename(file.filename),
            file_size_bytes=len(content_bytes),
            status=ProcessingStatus.PENDING.value,
            created_at=now,
            updated_at=now
        )

        db.add(submission)
        await db.flush()
        await db.refresh(submission)
        return submission

    @staticmethod
    async def get_submission(db: AsyncSession, submission_id: str) -> Optional[BugSubmission]:
        """Fetch a submission record by UUID."""
        query = select(BugSubmission).where(BugSubmission.id == submission_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_submissions(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[list[BugSubmission], int]:
        """List recent submissions with total count."""
        count_query = select(BugSubmission)
        count_res = await db.execute(count_query)
        total = len(count_res.scalars().all())

        query = select(BugSubmission).order_by(BugSubmission.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all()), total
