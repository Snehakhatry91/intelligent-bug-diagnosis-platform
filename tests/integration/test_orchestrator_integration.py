"""
Integration Tests for Multi-Agent Orchestrator
Tests end-to-end DAG execution, context assembly, telemetry recording,
and graceful fault isolation.
"""

from datetime import datetime, timezone
import pytest
from agents.orchestrator import orchestrator
from backend.models.schemas import InputType, ProcessingStatus, SubmissionResponse
from rag.vector_store import vector_store


@pytest.fixture(autouse=True)
def load_vector_index():
    vector_store.load()


@pytest.mark.asyncio
async def test_orchestrator_full_dag_execution():
    now = datetime.now(timezone.utc)
    submission = SubmissionResponse(
        id="orch-test-01",
        title="NullPointerException in RecordAccumulator",
        raw_content="java.lang.NullPointerException: cluster.partition() returned null\n\tat org.apache.kafka.clients.producer.KafkaProducer.send(KafkaProducer.java:820)",
        input_type=InputType.STACK_TRACE,
        status=ProcessingStatus.PENDING,
        created_at=now,
        updated_at=now
    )

    ctx = await orchestrator.execute_diagnosis(submission)

    # 1. Check all 6 stages executed
    assert ctx.submission_id == "orch-test-01"
    assert ctx.triage is not None
    assert ctx.log_analysis is not None
    assert ctx.duplicate_detection is not None
    assert ctx.root_cause is not None
    assert ctx.remediation is not None

    # 2. Check timeline recorded all stages
    stage_names = [s.stage_name for s in ctx.timeline]
    assert "Triage Agent" in stage_names
    assert "Log Analysis Agent" in stage_names
    assert "RAG Retrieval Engine" in stage_names
    assert "Duplicate Detection Agent" in stage_names
    assert "Root Cause Agent" in stage_names
    assert "Remediation Agent" in stage_names

    # 3. Check durations are non-negative
    for s in ctx.timeline:
        assert s.duration_ms >= 0.0

    # 4. Check completed_at timestamp populated
    assert ctx.completed_at is not None
