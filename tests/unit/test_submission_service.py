"""
Unit Tests for Submission Service & Input Validation
Tests sanitization, empty input handling, file type validation, size ceilings, and zero-execution policy.
"""

import io
import pytest
from pydantic import ValidationError
from fastapi import HTTPException, UploadFile
from backend.config import settings
from backend.models.schemas import InputType, SubmissionCreate
from backend.services.submission_service import SubmissionService


@pytest.mark.asyncio
async def test_sanitize_text_strips_null_bytes_and_control_chars():
    dirty_text = "Bug report\x00with null\x01bytes\x08and\x1fcontrols\nPreserves\tnewlines."
    cleaned = SubmissionService.sanitize_text(dirty_text)
    assert "\x00" not in cleaned
    assert "\x01" not in cleaned
    assert "\x08" not in cleaned
    assert "\x1f" not in cleaned
    assert "Bug reportwith nullbytesandcontrols\nPreserves\tnewlines." == cleaned


@pytest.mark.asyncio
async def test_submission_rejects_empty_or_short_title():
    with pytest.raises(ValidationError):
        SubmissionCreate(
            title="  ",
            raw_content="Valid crash content",
            input_type=InputType.BUG_REPORT
        )


@pytest.mark.asyncio
async def test_file_upload_rejects_unallowed_extension():
    dummy_file = UploadFile(
        filename="malicious_payload.exe",
        file=io.BytesIO(b"binary execution payload")
    )
    with pytest.raises(HTTPException) as exc_info:
        await SubmissionService.handle_file_upload(
            db=None,
            file=dummy_file
        )
    assert exc_info.value.status_code == 415
    assert "not permitted" in exc_info.value.detail


@pytest.mark.asyncio
async def test_file_upload_rejects_empty_file():
    empty_file = UploadFile(
        filename="empty.log",
        file=io.BytesIO(b"")
    )
    with pytest.raises(HTTPException) as exc_info:
        await SubmissionService.handle_file_upload(
            db=None,
            file=empty_file
        )
    assert exc_info.value.status_code == 422
    assert "empty" in exc_info.value.detail


@pytest.mark.asyncio
async def test_file_upload_enforces_5mb_ceiling():
    oversized_bytes = b"X" * (settings.MAX_FILE_SIZE_BYTES + 1)
    large_file = UploadFile(
        filename="giant.log",
        file=io.BytesIO(oversized_bytes)
    )
    with pytest.raises(HTTPException) as exc_info:
        await SubmissionService.handle_file_upload(
            db=None,
            file=large_file
        )
    assert exc_info.value.status_code == 413
    assert "exceeds maximum allowed size" in exc_info.value.detail
