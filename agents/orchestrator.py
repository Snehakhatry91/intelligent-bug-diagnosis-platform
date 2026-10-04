"""
Multi-Agent Orchestrator
Coordinates sequential DAG execution through specialized diagnostic agents:
1. Triage
2. Log Analysis
3. RAG Retrieval
4. Duplicate Detection
5. Root Cause
6. Remediation
Provides fault tolerance, state preservation on partial failures, and canonical context assembly.
"""

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
from agents.duplicate_detection_agent import duplicate_detection_agent
from agents.log_analysis_agent import log_analysis_agent
from agents.remediation_agent import remediation_agent
from agents.root_cause_agent import root_cause_agent
from agents.triage_agent import triage_agent
from backend.models.schemas import (
    BugAnalysisContext,
    DuplicateDetectionResult,
    HistoricalEvidenceItem,
    LogAnalysisResult,
    RemediationRecommendation,
    RootCauseResult,
    SubmissionResponse,
    TimelineStage,
    TriageResult,
)
from rag.retrieval_engine import retrieval_engine


class DiagnosticOrchestrator:
    """Manages the full end-to-end multi-agent pipeline."""

    async def execute_diagnosis(self, submission: SubmissionResponse) -> BugAnalysisContext:
        """
        Execute all 6 pipeline stages sequentially with fault isolation.
        Preserves intermediate state even if a downstream stage raises an error.
        """
        context = BugAnalysisContext(
            submission_id=submission.id,
            submission=submission,
            timeline=[],
            errors=[],
            created_at=datetime.now(timezone.utc)
        )

        # -------------------------------------------------------------
        # STAGE 1: Triage Agent
        # -------------------------------------------------------------
        triage_res, stage1 = await triage_agent.execute_with_telemetry(submission)
        context.timeline.append(stage1)
        if stage1.status == "completed" and triage_res:
            context.triage = triage_res
        else:
            context.errors.append(f"Stage 1 (Triage) warning: {stage1.notes}")

        # -------------------------------------------------------------
        # STAGE 2: Log Analysis Agent
        # -------------------------------------------------------------
        log_res, stage2 = await log_analysis_agent.execute_with_telemetry(submission)
        context.timeline.append(stage2)
        if stage2.status == "completed" and log_res:
            context.log_analysis = log_res
        else:
            context.errors.append(f"Stage 2 (Log Analysis) warning: {stage2.notes}")

        # -------------------------------------------------------------
        # STAGE 3: RAG Retrieval Engine
        # -------------------------------------------------------------
        t3_start = time.perf_counter()
        query_parts = [submission.title]
        if context.log_analysis and context.log_analysis.exception_type:
            query_parts.append(context.log_analysis.exception_type)
        if context.log_analysis and context.log_analysis.error_message:
            query_parts.append(context.log_analysis.error_message)
        if context.triage:
            query_parts.append(context.triage.affected_component)

        combined_query = " ".join(query_parts)
        try:
            evidence_items, rag_status = retrieval_engine.retrieve_evidence(combined_query, top_k=5)
            context.rag_retrieval = evidence_items
            duration_ms = (time.perf_counter() - t3_start) * 1000.0
            context.timeline.append(TimelineStage(
                stage_name="RAG Retrieval Engine",
                status="completed",
                duration_ms=round(duration_ms, 2),
                timestamp=datetime.now(timezone.utc),
                notes=rag_status
            ))
        except Exception as e:
            duration_ms = (time.perf_counter() - t3_start) * 1000.0
            context.timeline.append(TimelineStage(
                stage_name="RAG Retrieval Engine",
                status="failed",
                duration_ms=round(duration_ms, 2),
                timestamp=datetime.now(timezone.utc),
                notes=f"RAG retrieval error: {str(e)}"
            ))
            context.errors.append(f"Stage 3 (RAG) error: {str(e)}")

        # -------------------------------------------------------------
        # STAGE 4: Duplicate Detection Agent
        # -------------------------------------------------------------
        dup_res, stage4 = await duplicate_detection_agent.execute_with_telemetry(context.rag_retrieval)
        context.timeline.append(stage4)
        if stage4.status == "completed" and dup_res:
            context.duplicate_detection = dup_res
        else:
            context.errors.append(f"Stage 4 (Duplicate Detection) warning: {stage4.notes}")

        # -------------------------------------------------------------
        # STAGE 5: Root Cause Agent
        # -------------------------------------------------------------
        agent_payload = {
            "submission": submission,
            "triage": context.triage,
            "log_analysis": context.log_analysis,
            "rag_retrieval": context.rag_retrieval
        }
        rc_res, stage5 = await root_cause_agent.execute_with_telemetry(agent_payload)
        context.timeline.append(stage5)
        if stage5.status == "completed" and rc_res:
            context.root_cause = rc_res
        else:
            context.errors.append(f"Stage 5 (Root Cause) warning: {stage5.notes}")

        # -------------------------------------------------------------
        # STAGE 6: Remediation Agent
        # -------------------------------------------------------------
        rem_payload = {
            **agent_payload,
            "root_cause": context.root_cause
        }
        rem_res, stage6 = await remediation_agent.execute_with_telemetry(rem_payload)
        context.timeline.append(stage6)
        if stage6.status == "completed" and rem_res:
            context.remediation = rem_res
        else:
            context.errors.append(f"Stage 6 (Remediation) warning: {stage6.notes}")

        context.completed_at = datetime.now(timezone.utc)
        return context


orchestrator = DiagnosticOrchestrator()
