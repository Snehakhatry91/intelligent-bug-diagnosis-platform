"""
Unit Tests for Specialized Diagnostic Agents
Validates Triage variability, Duplicate gating, Root Cause 4-tier attribution,
and Remediation recommendation generation.
"""

from datetime import datetime, timezone
import pytest
from agents.duplicate_detection_agent import duplicate_detection_agent
from agents.remediation_agent import remediation_agent
from agents.root_cause_agent import root_cause_agent
from agents.triage_agent import triage_agent
from backend.models.schemas import (
    DuplicateClassification,
    HistoricalEvidenceItem,
    InputType,
    LogAnalysisResult,
    PriorityLevel,
    ProcessingStatus,
    SeverityLevel,
    SubmissionResponse,
)


def make_test_submission(title: str, content: str) -> SubmissionResponse:
    now = datetime.now(timezone.utc)
    return SubmissionResponse(
        id="test-sub-uuid",
        title=title,
        raw_content=content,
        input_type=InputType.BUG_REPORT,
        status=ProcessingStatus.PENDING,
        created_at=now,
        updated_at=now
    )


@pytest.mark.asyncio
async def test_triage_agent_produces_variable_severities_and_confidences():
    # Critical case
    crit_sub = make_test_submission("Fatal deadlock in database engine", "System crash with SIGSEGV and data corruption.")
    crit_res = await triage_agent.process(crit_sub)
    assert crit_res.severity == SeverityLevel.CRITICAL
    assert crit_res.confidence >= 0.90

    # Low case
    low_sub = make_test_submission("Minor typo in layout footer", "Cosmetic typo on user interface button label.")
    low_res = await triage_agent.process(low_sub)
    assert low_res.severity == SeverityLevel.LOW
    assert low_res.confidence <= 0.80

    # Ensure agent returns distinct values and NOT static 0.95
    assert crit_res.confidence != low_res.confidence
    assert crit_res.severity != low_res.severity


@pytest.mark.asyncio
async def test_duplicate_detection_agent_threshold_gating():
    # Item with score >= 0.82
    high_dup_evidence = [
        HistoricalEvidenceItem(
            issue_id="KAFKA-10134",
            project="Apache",
            title="High CPU issue during rebalance in Kafka consumer after upgrading to 2.5",
            similarity_score=0.88,
            classification=DuplicateClassification.LIKELY_DUPLICATE
        )
    ]
    res_dup = await duplicate_detection_agent.process(high_dup_evidence)
    assert res_dup.is_duplicate is True
    assert "Likely duplicate detected" in res_dup.summary

    # Item with score 0.72 (Related, not duplicate)
    related_evidence = [
        HistoricalEvidenceItem(
            issue_id="HTTPCLIENT-2099",
            project="Apache",
            title="SocketTimeoutException during connection release in pool manager",
            similarity_score=0.72,
            classification=DuplicateClassification.RELATED_ISSUE
        )
    ]
    res_rel = await duplicate_detection_agent.process(related_evidence)
    assert res_rel.is_duplicate is False
    assert "Not classified as duplicate" in res_rel.summary


@pytest.mark.asyncio
async def test_root_cause_agent_four_tier_attribution():
    sub = make_test_submission("NullPointerException in payment", "PaymentMethod is null")
    log_res = LogAnalysisResult(
        exception_type="java.lang.NullPointerException",
        error_message="PaymentMethod is null",
        failure_point="PaymentService.java:42",
        raw_extracted_facts=["Parsed exception signature: NullPointerException"]
    )
    context_dict = {
        "submission": sub,
        "triage": None,
        "log_analysis": log_res,
        "rag_retrieval": []
    }
    rc_res = await root_cause_agent.process(context_dict)
    assert rc_res.hypothesis != ""
    assert len(rc_res.observed_facts) > 0
    assert "Insufficient historical evidence found." in rc_res.historical_evidence
    assert rc_res.evidence_status == "insufficient"
    assert len(rc_res.ai_inference) > 0


@pytest.mark.asyncio
async def test_remediation_agent_generates_concrete_patch_and_tests():
    sub = make_test_submission("NullPointerException in payment", "PaymentMethod is null")
    log_res = LogAnalysisResult(
        exception_type="java.lang.NullPointerException",
        error_message="PaymentMethod is null",
        failure_point="PaymentService.java:42"
    )
    context_dict = {
        "submission": sub,
        "triage": None,
        "log_analysis": log_res,
        "rag_retrieval": [],
        "root_cause": None
    }
    rem_res = await remediation_agent.process(context_dict)
    assert rem_res.action != ""
    assert rem_res.code_patch is not None
    assert len(rem_res.recommended_tests) > 0
