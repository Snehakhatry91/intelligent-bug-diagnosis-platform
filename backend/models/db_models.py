"""
SQLAlchemy ORM Models
Defines persisted entities for bug submissions, historical defect repository,
analysis outputs, and human-verified knowledge base entries.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.database import Base


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class BugSubmission(Base):
    __tablename__ = "bug_submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    raw_content = Column(Text, nullable=False)
    input_type = Column(String(50), nullable=False, default="bug_report")
    environment_details = Column(String(1000), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    analysis_results = relationship("AnalysisResultRecord", back_populates="submission", cascade="all, delete-orphan")


class HistoricalDefect(Base):
    __tablename__ = "historical_defects"

    issue_id = Column(String(100), primary_key=True)
    project = Column(String(100), nullable=False)
    source = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    component = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    resolution = Column(String(100), nullable=False)
    fix_patch_summary = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class AnalysisResultRecord(Base):
    __tablename__ = "analysis_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String(36), ForeignKey("bug_submissions.id"), nullable=False, unique=True)
    severity = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    affected_component = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    exception_type = Column(String(150), nullable=True)
    error_message = Column(Text, nullable=True)
    failure_point = Column(Text, nullable=True)
    affected_code_path = Column(Text, nullable=True)
    root_cause_hypothesis = Column(Text, nullable=False)
    root_cause_confidence = Column(Float, nullable=False)
    is_duplicate = Column(Boolean, nullable=False, default=False)
    top_duplicate_id = Column(String(100), nullable=True)
    top_duplicate_score = Column(Float, nullable=True)
    canonical_context_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    submission = relationship("BugSubmission", back_populates="analysis_results")


class KnowledgeBaseEntry(Base):
    __tablename__ = "knowledge_base_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String(36), nullable=False)
    title = Column(String(255), nullable=False)
    component = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    root_cause = Column(Text, nullable=False)
    resolution = Column(Text, nullable=False)
    verified_by = Column(String(100), nullable=False)
    verification_notes = Column(Text, nullable=False)
    verified_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    vector_indexed = Column(Boolean, default=True, nullable=False)
