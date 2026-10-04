"""
Canonical Data Schemas and DTO Models (Pydantic v2)
Implements strongly typed structures including BugAnalysisContext, agent results,
and API request/response payloads.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


# =====================================================================
# ENUMS
# =====================================================================

class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class PriorityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InputType(str, Enum):
    BUG_REPORT = "bug_report"
    STACK_TRACE = "stack_trace"
    ERROR_LOG = "error_log"
    FILE_UPLOAD = "file_upload"


class DuplicateClassification(str, Enum):
    LIKELY_DUPLICATE = "Likely Duplicate"
    RELATED_ISSUE = "Related Issue"
    WEAK_MATCH = "Weak Match"
    NO_MATCH = "No Match"


# =====================================================================
# SUBMISSION SCHEMAS
# =====================================================================

class SubmissionCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=250, description="Brief summary of the defect")
    raw_content: str = Field(..., min_length=5, description="Full bug report, stack trace, or log text")
    input_type: InputType = Field(default=InputType.BUG_REPORT)
    environment_details: Optional[str] = Field(default=None, max_length=1000)
    file_name: Optional[str] = Field(default=None)


class SubmissionResponse(BaseModel):
    id: str
    title: str
    raw_content: str
    input_type: InputType
    environment_details: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# AGENT RESULT SCHEMAS
# =====================================================================

class TriageResult(BaseModel):
    severity: SeverityLevel
    priority: PriorityLevel
    affected_component: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    signals: List[str] = Field(default_factory=list)


class StackFrame(BaseModel):
    file: str
    line: Optional[int] = None
    function: Optional[str] = None
    code_context: Optional[str] = None


class LogAnalysisResult(BaseModel):
    exception_type: Optional[str] = None
    error_message: Optional[str] = None
    failure_point: Optional[str] = None
    affected_code_path: Optional[str] = None
    key_log_signals: List[str] = Field(default_factory=list)
    stack_frames: List[StackFrame] = Field(default_factory=list)
    raw_extracted_facts: List[str] = Field(default_factory=list)
    parsing_notes: str = ""


class HistoricalEvidenceItem(BaseModel):
    issue_id: str
    project: str
    title: str
    similarity_score: float
    classification: DuplicateClassification
    resolution: Optional[str] = None
    fix_patch_summary: Optional[str] = None
    source_url: Optional[str] = None
    component: Optional[str] = None


class DuplicateDetectionResult(BaseModel):
    is_duplicate: bool
    top_matches: List[HistoricalEvidenceItem] = Field(default_factory=list)
    duplicate_threshold: float
    related_threshold: float
    summary: str


class RootCauseResult(BaseModel):
    hypothesis: str
    confidence: float = Field(ge=0.0, le=1.0)
    observed_facts: List[str] = Field(default_factory=list)
    historical_evidence: List[str] = Field(default_factory=list)
    ai_inference: List[str] = Field(default_factory=list)
    evidence_status: str = "sufficient"  # "sufficient" or "insufficient"


class RecommendedTest(BaseModel):
    test_type: str  # "Unit Test", "Integration Test", "Regression Test"
    description: str
    test_code_or_command: Optional[str] = None


class RemediationRecommendation(BaseModel):
    action: str
    explanation: str
    affected_area: str
    implementation_guidance: str
    supporting_evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_tests: List[RecommendedTest] = Field(default_factory=list)
    code_patch: Optional[str] = None


class TimelineStage(BaseModel):
    stage_name: str
    status: str  # "completed", "failed", "skipped"
    duration_ms: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None


# =====================================================================
# CANONICAL BUG ANALYSIS CONTEXT
# =====================================================================

class BugAnalysisContext(BaseModel):
    """
    Canonical strongly-typed analysis context passed through the multi-agent DAG.
    Maintains all intermediate and final outputs of triage, log analysis, RAG,
    root cause identification, duplicate detection, and remediation.
    """
    submission_id: str
    submission: SubmissionResponse
    triage: Optional[TriageResult] = None
    log_analysis: Optional[LogAnalysisResult] = None
    rag_retrieval: List[HistoricalEvidenceItem] = Field(default_factory=list)
    duplicate_detection: Optional[DuplicateDetectionResult] = None
    root_cause: Optional[RootCauseResult] = None
    remediation: Optional[RemediationRecommendation] = None
    timeline: List[TimelineStage] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# HISTORICAL DEFECT SCHEMA (Canonical Dataset Model)
# =====================================================================

class HistoricalDefectSchema(BaseModel):
    issue_id: str
    project: str
    source: str
    title: str
    description: str
    component: str
    severity: str
    priority: str
    status: str
    resolution: str
    fix_patch_summary: str
    source_url: str
    created_at: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# KNOWLEDGE BASE GROWTH SCHEMA
# =====================================================================

class KBVerificationRequest(BaseModel):
    analysis_id: str
    verified_by: str
    verification_notes: str
    confirmed_root_cause: str
    confirmed_resolution: str


class KBEntryResponse(BaseModel):
    id: str
    submission_id: str
    title: str
    component: str
    severity: str
    root_cause: str
    resolution: str
    verified_by: str
    verification_notes: str
    verified_at: datetime
    vector_indexed: bool

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# ANALYTICS RECONCILIATION SCHEMAS
# =====================================================================

class DistributionCount(BaseModel):
    name: str
    count: int
    percentage: float


class AnalyticsSummary(BaseModel):
    total_submissions: int
    completed_analyses: int
    pending_analyses: int
    failed_analyses: int
    verified_kb_entries: int
    historical_corpus_size: int
    duplicate_rate_percentage: float

    # Strictly reconciled distributions
    severity_distribution: List[DistributionCount]
    priority_distribution: List[DistributionCount]
    component_distribution: List[DistributionCount]
    exception_distribution: List[DistributionCount]
    reconciliation_verified: bool
