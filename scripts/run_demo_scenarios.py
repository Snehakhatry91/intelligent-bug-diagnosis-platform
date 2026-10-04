"""
Demonstration Scenarios Runner
Executes the five mandatory synthetic failure modes end-to-end:
1. NullPointerException
2. Database Connection Failure & Deadlock
3. JWT Authentication Failure
4. API / Network Timeout
5. OutOfMemory Resource Exhaustion
Passes each through Submission -> Triage -> Log Analysis -> RAG -> Duplicate Detection -> Root Cause -> Remediation.
"""

import asyncio
import json
from pathlib import Path
import sys
import time

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import settings
from backend.database import AsyncSessionLocal, init_db
from backend.models.schemas import InputType, ProcessingStatus, SubmissionCreate, SubmissionResponse
from backend.models.db_models import AnalysisResultRecord, BugSubmission
from backend.services.submission_service import SubmissionService
from agents.orchestrator import orchestrator
from rag.vector_store import vector_store


async def run_demos():
    print("=" * 70)
    print("EXECUTING FIVE REQUIRED SYNTHETIC DEMONSTRATION SCENARIOS")
    print("=" * 70)

    await init_db()
    vector_store.load()
    if not vector_store.is_ready():
        print("Vector index not found. Run:\npython scripts/ingest_historical_data.py", file=sys.stderr)
        sys.exit(1)
    print(f"[OK] Vector index loaded ({vector_store.count()} chunks)")

    fixture_path = BASE_DIR / "tests" / "fixtures" / "demo_scenarios.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    results = []

    async with AsyncSessionLocal() as session:
        for idx, sc in enumerate(scenarios, 1):
            print(f"\n[{idx}/5] Scenario {sc['scenario_id']}: {sc['name']}")
            print("-" * 60)

            # 1. Submission
            sub_create = SubmissionCreate(
                title=sc["title"],
                raw_content=sc["raw_content"],
                input_type=InputType(sc["input_type"]),
                environment_details=sc["environment_details"]
            )
            submission_record = await SubmissionService.create_submission(session, sub_create)
            await session.commit()
            print(f"  * Submission ID: {submission_record.id}")
            print(f"  * Input Type:    {submission_record.input_type}")

            # 2. End-to-End Orchestration
            t0 = time.perf_counter()
            sub_dto = SubmissionResponse.model_validate(submission_record)
            context = await orchestrator.execute_diagnosis(sub_dto)
            total_duration_ms = (time.perf_counter() - t0) * 1000.0

            # 3. Print Outputs of Each Agent Stage
            triage = context.triage
            log_res = context.log_analysis
            dup_res = context.duplicate_detection
            rc_res = context.root_cause
            rem_res = context.remediation

            print(f"  * Triage:        Severity={triage.severity.value} | Priority={triage.priority.value} | Conf={triage.confidence}")
            print(f"                   Component: {triage.affected_component}")
            print(f"  * Log Analysis:  Exception={log_res.exception_type} | Failure Point={log_res.failure_point}")
            print(f"  * RAG Retrieval: Found {len(context.rag_retrieval)} historical evidence match(es)")
            for ev in context.rag_retrieval[:2]:
                print(f"                   -> [{ev.project} {ev.issue_id}] Sim: {ev.similarity_score * 100:.1f}% ({ev.classification.value})")

            print(f"  * Duplicate Det: Duplicate={dup_res.is_duplicate} | Top Match Score={dup_res.top_matches[0].similarity_score if dup_res.top_matches else 'N/A'}")
            print(f"  * Root Cause:    Hypothesis: {rc_res.hypothesis[:85]}... (Conf: {rc_res.confidence})")
            print(f"                   Evidence Status: {rc_res.evidence_status}")
            print(f"  * Remediation:   Action: {rem_res.action}")
            print(f"                   Tests: {len(rem_res.recommended_tests)} test(s) recommended")
            print(f"  * Execution Time: {total_duration_ms:.1f}ms across 6 stages")

            # 4. Persist Analysis Record
            top_dup = dup_res.top_matches[0] if dup_res.top_matches else None
            record = AnalysisResultRecord(
                submission_id=submission_record.id,
                severity=triage.severity.value,
                priority=triage.priority.value,
                affected_component=triage.affected_component,
                confidence=triage.confidence,
                exception_type=log_res.exception_type,
                error_message=log_res.error_message,
                failure_point=log_res.failure_point,
                affected_code_path=log_res.affected_code_path,
                root_cause_hypothesis=rc_res.hypothesis,
                root_cause_confidence=rc_res.confidence,
                is_duplicate=dup_res.is_duplicate,
                top_duplicate_id=top_dup.issue_id if top_dup else None,
                top_duplicate_score=top_dup.similarity_score if top_dup else None,
                canonical_context_json=context.model_dump_json()
            )
            session.add(record)
            submission_record.status = ProcessingStatus.COMPLETED.value
            await session.commit()

            results.append({
                "scenario_id": sc["scenario_id"],
                "name": sc["name"],
                "duration_ms": total_duration_ms,
                "severity": triage.severity.value,
                "priority": triage.priority.value,
                "is_duplicate": dup_res.is_duplicate,
                "status": "PASS"
            })

    print("\n" + "=" * 70)
    print("FIVE DEMO SCENARIOS SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Scenario':<12} | {'Name':<35} | {'Severity':<10} | {'Dup?':<6} | {'Latency':<8} | {'Status'}")
    print("-" * 70)
    for r in results:
        print(f"{r['scenario_id']:<12} | {r['name']:<35} | {r['severity']:<10} | {str(r['is_duplicate']):<6} | {r['duration_ms']:.1f}ms | {r['status']}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_demos())
